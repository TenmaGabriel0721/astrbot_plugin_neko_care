import asyncio
import random
import re
import time
from pathlib import Path
from typing import Optional

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register, StarTools
from astrbot.core.star.filter.command import GreedyStr

try:
    from astrbot.api.message_components import Plain, Image
except Exception:
    Plain = None
    Image = None

from .storage import JsonStore
from .economy import EconomyService
from .sign import SignService
from .catgirl import CatgirlService
from .runtime_config import NekoRuntimeConfig


PLUGIN_NAME = "astrbot_plugin_neko_care"
KEYWORD_TRIGGER_ENABLED = True
PENDING_IMAGE_CHANGES = {}


def pending_image_filter():
    class PendingImageFilter(filter.CustomFilter):
        def filter(self, event: AstrMessageEvent, cfg) -> bool:
            uid = str(event.get_sender_id())
            if uid not in PENDING_IMAGE_CHANGES:
                return False
            event.is_at_or_wake_command = True
            event.is_wake = True
            return True

    return PendingImageFilter


def keyword_command_filter(*command_names: str):
    class KeywordCommandFilter(filter.CustomFilter):
        def filter(self, event: AstrMessageEvent, cfg) -> bool:
            if event.is_at_or_wake_command:
                return True
            if not KEYWORD_TRIGGER_ENABLED:
                return True

            message = re.sub(r"\s+", " ", event.get_message_str().strip())
            for command_name in command_names:
                if message == command_name or message.startswith(f"{command_name} "):
                    event.is_at_or_wake_command = True
                    event.is_wake = True
                    return True
            return True

    return KeywordCommandFilter


def neko_command(command_name: str, alias: set | None = None, **kwargs):
    command_names = [command_name, *(alias or set())]

    def decorator(awaitable):
        awaitable = filter.custom_filter(keyword_command_filter(*command_names), False)(awaitable)
        return filter.command(command_name, alias=alias, **kwargs)(awaitable)

    return decorator

@register("astrbot_plugin_neko_care", "若梦&TenmaGabriel0721", "猫娘羁绊养成、签到打工", "1.4.6")
class SapphireEconomyPlugin(Star):
    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        self.config = config or {}

        self.coin_name = str(self.config.get("coin_name", "宝石"))[:16] or "宝石"
        self.sign_mode = "图片签到" if self.config.get("sign_mode", "图片签到") in ("图片签到", "image") else "文字签到"
        self.keyword_trigger_enabled = bool(self.config.get("keyword_trigger_enabled", True))
        global KEYWORD_TRIGGER_ENABLED
        KEYWORD_TRIGGER_ENABLED = self.keyword_trigger_enabled

        self.sign_min = max(0, int(self.config.get("sign_min_reward", 65)))
        self.sign_max = max(self.sign_min, int(self.config.get("sign_max_reward", 125)))
        self.work_min = max(0, int(self.config.get("work_min_reward", 35)))
        self.work_max = max(self.work_min, int(self.config.get("work_max_reward", 85)))

        self.extra_admin_ids = set(str(x) for x in self.config.get("extra_admin_ids", []))
        self.wish_probability = min(1.0, max(0.0, float(self.config.get("catgirl_wish_probability", 0.8))))
        self.wish_pity = max(1, int(self.config.get("catgirl_wish_pity", 3)))
        self.appearance_change_price = max(0, int(self.config.get("appearance_change_price", 900)))

        base_dir = Path(__file__).resolve().parent
        self.base_dir = base_dir
        self.asset_dir = base_dir / "assets"
        self.font_dir = base_dir / "fonts"
        self.catgirl_dir = self.asset_dir / "catgirl_pool"
        self.background_dir = self.asset_dir / "sign_backgrounds"
        self.quote_file = self.asset_dir / "quotes.txt"

        try:
            astrbot_data_dir = base_dir.parent.parent
            self.data_dir = astrbot_data_dir / "plugin_data" / PLUGIN_NAME
        except Exception:
            self.data_dir = base_dir / "plugin_data"

        self.upload_dir = self.data_dir / "pic"
        self.cache_dir = self.data_dir / "cache"

        for d in [self.asset_dir, self.font_dir, self.catgirl_dir, self.background_dir, self.data_dir, self.upload_dir, self.cache_dir]:
            Path(d).mkdir(parents=True, exist_ok=True)

        self._ensure_default_quote_file()

        self.store = JsonStore(self.data_dir / "store.json")
        self.runtime_config = NekoRuntimeConfig(self.data_dir / "runtime_config.json", self.config)
        self._apply_runtime_config()

        self.economy = EconomyService(self.store, self.coin_name, self.work_min, self.work_max, self.runtime_config.snapshot)
        self.sign = SignService(
            self.store, self.economy, self.coin_name, self.sign_min, self.sign_max,
            self.base_dir, self.background_dir, self.font_dir, self.cache_dir, self.quote_file, self.runtime_config.snapshot
        )
        self.catgirl = CatgirlService(
            self.store, self.economy, self.coin_name, self.base_dir, self.catgirl_dir,
            self.upload_dir, self.font_dir, self.cache_dir, self.wish_probability, self.wish_pity, self.appearance_change_price,
            self.runtime_config.snapshot
        )
        self.page_api = None
        self._register_page_api_if_available()

        self._pending_adoptions = {}
        global PENDING_IMAGE_CHANGES
        self._pending_image_changes = PENDING_IMAGE_CHANGES
        self._background_tasks = set()

    def _runtime_snapshot(self) -> dict:
        runtime_config = getattr(self, "runtime_config", None)
        if runtime_config is None:
            return {}
        try:
            return runtime_config.snapshot()
        except Exception:
            return {}

    def _apply_runtime_config(self) -> None:
        data = self._runtime_snapshot()
        economy = data.get("economy", {}) if isinstance(data.get("economy"), dict) else {}
        wish = data.get("wish", {}) if isinstance(data.get("wish"), dict) else {}
        self.coin_name = str(economy.get("coin_name") or self.coin_name or "宝石")[:16] or "宝石"
        self.sign_min = max(0, int(economy.get("sign_min_reward", self.sign_min)))
        self.sign_max = max(self.sign_min, int(economy.get("sign_max_reward", self.sign_max)))
        self.work_min = max(0, int(economy.get("daily_work_min_reward", self.work_min)))
        self.work_max = max(self.work_min, int(economy.get("daily_work_max_reward", self.work_max)))
        self.wish_probability = min(1.0, max(0.0, float(wish.get("probability", self.wish_probability))))
        self.wish_pity = max(1, int(wish.get("pity", self.wish_pity)))
        self.appearance_change_price = max(0, int(wish.get("appearance_change_price", self.appearance_change_price)))

        for service in (getattr(self, "economy", None), getattr(self, "sign", None), getattr(self, "catgirl", None)):
            if service is not None and hasattr(service, "coin_name"):
                service.coin_name = self.coin_name

    def _coin_name(self) -> str:
        data = self._runtime_snapshot()
        economy = data.get("economy", {}) if isinstance(data.get("economy"), dict) else {}
        return str(economy.get("coin_name") or self.coin_name or "宝石")

    def _care_rules(self) -> dict:
        data = self._runtime_snapshot()
        care = data.get("care", {}) if isinstance(data.get("care"), dict) else {}
        return care

    def _wish_rules(self) -> tuple[float, int, int]:
        data = self._runtime_snapshot()
        wish = data.get("wish", {}) if isinstance(data.get("wish"), dict) else {}
        return (
            min(1.0, max(0.0, float(wish.get("probability", self.wish_probability)))),
            max(1, int(wish.get("pity", self.wish_pity))),
            max(0, int(wish.get("appearance_change_price", self.appearance_change_price))),
        )

    def _register_page_api_if_available(self) -> None:
        try:
            if not callable(getattr(self.context, "register_web_api", None)):
                return
            from .page_api import NekoCarePageApi

            self.page_api = NekoCarePageApi(self)
            self.page_api.register_routes()
        except Exception:
            self.page_api = None

    def _ensure_default_quote_file(self):
        if self.quote_file.exists():
            return
        self.quote_file.parent.mkdir(parents=True, exist_ok=True)
        self.quote_file.write_text(
            "愿你今天也被温柔以待。\n"
            "要把普通的日子过得浪漫一点。\n"
            "慢慢来，好运正在路上。\n"
            "心里装着小星星，生活才会亮晶晶。\n"
            "今天也要好好吃饭，好好睡觉。\n"
            "猫猫偷偷告诉你：今天会有好事发生。\n"
            "每一次签到，都是和幸运打了个招呼。|小助手\n",
            encoding="utf-8",
        )

    def _uid(self, event: AstrMessageEvent) -> str:
        return str(event.get_sender_id())

    def _gid(self, event: AstrMessageEvent) -> str:
        gid = event.get_group_id()
        return f"group_{gid}" if gid else f"private_{event.get_sender_id()}"

    def _name(self, event: AstrMessageEvent) -> str:
        try:
            return event.get_sender_name()
        except Exception:
            return str(event.get_sender_id())

    def _is_admin(self, event: AstrMessageEvent) -> bool:
        uid = str(event.get_sender_id())
        if uid in self.extra_admin_ids:
            return True
        for attr in ("is_admin", "is_superuser"):
            checker = getattr(event, attr, None)
            if callable(checker):
                try:
                    if checker():
                        return True
                except Exception:
                    pass
        try:
            role = str(getattr(event, "role", "") or getattr(event, "sender_role", "")).lower()
            return role in ("admin", "administrator", "owner", "superuser")
        except Exception:
            return False

    def _extract_at_uid(self, event: AstrMessageEvent) -> Optional[str]:
        try:
            msg = event.message_obj.message
            for seg in msg:
                seg_type = str(getattr(seg, "type", "")).lower()
                data = getattr(seg, "data", {}) or {}
                if seg_type == "at":
                    target = data.get("qq") or data.get("user_id") or data.get("id")
                    if target and str(target) != "all":
                        return str(target)
        except Exception:
            pass
        text = event.message_str or ""
        m = re.search(r"@(\d+)", text)
        return m.group(1) if m else None

    def _extract_first_image(self, event: AstrMessageEvent) -> Optional[str]:
        def pick_from_data(data: dict):
            if not isinstance(data, dict):
                return None
            return (
                data.get("url")
                or data.get("path")
                or data.get("src")
                or data.get("file")
                or data.get("file_id")
            )

        try:
            msg = event.message_obj.message
            for seg in msg:
                if isinstance(seg, dict):
                    seg_type = str(seg.get("type", "")).lower()
                    data = seg.get("data", {}) or {}
                else:
                    seg_type = str(getattr(seg, "type", "") or seg.__class__.__name__).lower()
                    data = getattr(seg, "data", None) or {
                        "url": getattr(seg, "url", None),
                        "file": getattr(seg, "file", None),
                        "path": getattr(seg, "path", None),
                        "src": getattr(seg, "src", None),
                        "file_id": getattr(seg, "file_id", None),
                    }

                if "image" in seg_type or seg_type in ("图片",):
                    result = pick_from_data(data)
                    if result:
                        return str(result)
        except Exception:
            pass

        raw = str(getattr(event.message_obj, "raw_message", "") or event.message_str or "")
        match = re.search(r"\[CQ:image,[^\]]*(?:url|file)=([^,\]]+)", raw)
        return match.group(1) if match else None


    def _mixed_result(self, event: AstrMessageEvent, text: str, img_path: Optional[Path] = None):
        if img_path:
            try:
                return event.image_result(str(img_path))
            except Exception:
                pass
        return event.plain_result(text)

    async def _auto_finalize_adoption(self, uid: str, token: str, gid: str):
        await asyncio.sleep(120)
        key = uid
        pending = self._pending_adoptions.get(key)
        if not pending or pending.get("token") != token:
            return
        self.catgirl.finalize_adoption(gid, uid, choice="first")
        self._pending_adoptions.pop(key, None)

    @neko_command("猫猫帮助", alias={"猫娘帮助"}, desc="查看猫娘养成插件的图片帮助菜单和所有指令说明")
    async def catgirl_help(self, event: AstrMessageEvent):
        coin_name = self._coin_name()
        wish_probability, wish_pity, appearance_price = self._wish_rules()
        care = self._care_rules()
        feed_limit = care.get("feed_satiety_limit", 85)
        satiety_minutes = int(float(care.get("satiety_decay_minutes", 2880)))
        runaway_hours = float(care.get("runaway_after_zero_hours", 24))
        help_sections = [
            ("基础经济", [
                ("签到 / 猫猫签到", "每日领取宝石"),
                ("每日打工", "主人每日收入"),
                ("查看猫猫钱包", "查看余额"),
                ("钱包转账 数量 @用户", "转出宝石"),
            ]),
            ("收养与状态", [
                ("请赐我一只可爱猫娘吧", "每日许愿"),
                ("带她回家 / 确认收养", "确认候选"),
                ("换一只猫娘 / 换个形象", "切换候选"),
                ("成长档案 / 猫猫状态", "状态档案"),
            ]),
            ("照顾与互动", [
                ("喂猫 / 喂猫猫", "喂食恢复"),
                ("撸猫 / 逗猫 / 摸猫", "内置互动"),
                ("rua猫 / 陪猫娘", "内置互动"),
                ("猫娘互动 动作名", "自定义互动"),
            ]),
            ("猫娘打工", [
                ("猫娘打工", "领取或随机打工"),
                ("猫娘打工 地点名", "指定地点"),
                ("猫娘打工 列表", "查看全量地点"),
                ("猫娘打工 解锁 地点名", "解锁地点"),
            ]),
            ("商店与护理", [
                ("猫娘商店 [分类]", "查看道具"),
                ("购买 道具名 [数量]", "购买道具"),
                ("背包 / 猫娘背包", "查看道具"),
                ("使用 道具名", "使用道具"),
                ("猫娘护理 [服务名]", "购买护理"),
            ]),
            ("档案与排行", [
                ("猫娘改名 名字", "消耗改名卡"),
                ("更换猫娘形象", "上传新图片"),
                ("羁绊排行榜", "本群排行"),
                ("钱包排行榜", "余额排行"),
                ("迁移猫娘到本群", "登记群排行"),
            ]),
            ("管理员", [
                ("管理员给 数量 @用户", "增加宝石"),
                ("管理员扣 数量 @用户", "扣除宝石"),
                ("管理员查看 @用户", "查看余额"),
            ]),
        ]
        text = (
            "猫猫小助手来啦 ฅ^•ﻌ•^ฅ\n\n"
            "指令说明：\n"
            + "\n".join(
                f"{title}\n" + "\n".join(f"- {command}：{desc}" for command, desc in rows)
                for title, rows in help_sections
            ) + "\n\n"
            "许愿说明：\n"
            f"每天许愿有 {int(wish_probability * 100)}% 概率遇见猫娘，{wish_pity} 次内必定成功喔～\n\n"
            "喂养说明：\n"
            f"状态按分钟结算，饱食度低于 {round(feed_limit)} 时可以喂猫。\n"
            f"饱食度约 {round(satiety_minutes / 60)} 小时从 100 降到 0，归零超过 {round(runaway_hours)} 小时会离家出走。"
        )
        card = self.catgirl.draw_section_card(
            "猫猫帮助",
            subtitle="指令说明与用法",
            sections=help_sections,
            metrics=[
                ("许愿概率", f"{int(wish_probability * 100)}%"),
                ("许愿保底", f"{wish_pity} 次"),
                ("喂食阈值", f"{round(feed_limit)}"),
                ("饱食清零", f"约 {round(satiety_minutes / 60)} 小时"),
                ("离家倒计时", f"{round(runaway_hours)} 小时"),
                ("形象价格", f"{appearance_price} {coin_name}"),
            ],
            footer="状态相关输出、帮助菜单、商店、背包、护理和打工列表均使用图片展示。",
            tag="help",
        )
        yield self._mixed_result(event, text, card)

    @neko_command("查看猫猫钱包", alias={"查看猫娘钱包"}, desc="查看自己的宝石余额")
    async def my_wallet(self, event: AstrMessageEvent):
        uid = self._uid(event)
        bal = self.economy.get_balance(uid)
        yield event.plain_result(f"你的小钱包里有 {bal} {self._coin_name()} 喔～")

    @neko_command("钱包转账", desc="钱包转账 数量 @用户：把宝石转给指定用户")
    async def wallet_transfer(self, event: AstrMessageEvent, amount: int):
        uid = self._uid(event)
        target = self._extract_at_uid(event)
        if not target:
            yield event.plain_result("要 @ 想转账的小伙伴喔～")
            return
        ok, msg = self.economy.transfer(uid, target, amount)
        yield event.plain_result(msg)

    @neko_command("每日打工", desc="主人每日打工获得宝石，每天一次")
    async def daily_work(self, event: AstrMessageEvent):
        uid = self._uid(event)
        ok, msg = self.economy.daily_work(uid)
        yield event.plain_result(msg)

    @neko_command("签到", alias={"猫猫签到"}, desc="每日签到领取宝石和签到卡片")
    async def sign_entry(self, event: AstrMessageEvent):
        uid = self._uid(event)
        name = self._name(event)
        ok, data_or_msg = self.sign.sign(uid, name)
        if not ok:
            yield event.plain_result(data_or_msg)
            return

        data = data_or_msg
        if self.sign_mode == "图片签到":
            try:
                img_path = self.sign.draw_sign(uid, name, data["inc"], data["balance"], data["count"], data.get("quote", ""), data.get("quote_from", ""))
                yield event.image_result(str(img_path))
                return
            except Exception as e:
                coin_name = self._coin_name()
                yield event.plain_result(f"签到成功啦，但图片生成失败：{e}\n你获得了 {data['inc']} {coin_name}，现在有 {data['balance']} {coin_name} 喔～")
                return

        quote_line = data.get("quote", "")
        quote_from = data.get("quote_from", "")
        if quote_from:
            quote_line = f"{quote_line}\n—— {quote_from}"
        coin_name = self._coin_name()
        yield event.plain_result(f"签到成功喵～ ฅ^•ﻌ•^ฅ\n今天捡到了 {data['inc']} {coin_name}！\n小钱包里现在有 {data['balance']} {coin_name} 啦～\n\n今日一言：\n{quote_line}")

    @neko_command("请赐我一只可爱猫娘吧", desc="每日许愿收养猫娘，失败会累计保底")
    async def wish_catgirl(self, event: AstrMessageEvent):
        uid = self._uid(event)
        gid = self._gid(event)
        ok, status, msg, first, second = self.catgirl.prepare_wish(uid, gid)
        if not ok:
            yield event.plain_result(msg)
            return

        token = f"{time.time()}:{random.random()}"
        self._pending_adoptions[uid] = {
            "token": token,
            "uid": uid,
            "gid": gid,
            "first": first,
            "second": second,
            "expire": time.time() + 120,
        }
        task = asyncio.create_task(self._auto_finalize_adoption(uid, token, gid))
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        img = self.catgirl.draw_wish_card(first)
        yield self._mixed_result(event, msg, img)

    @neko_command("带她回家", alias={"确认收养", "换一只猫娘", "换个形象"}, desc="确认收养当前猫娘，或切换另一个候选猫娘")
    async def confirm_catgirl_adoption(self, event: AstrMessageEvent):
        uid = self._uid(event)
        gid = self._gid(event)
        raw = (event.message_str or "").strip()
        pending = self._pending_adoptions.get(uid) or self.catgirl.get_pending_adoption(uid)
        if not pending:
            return

        choice = "second" if raw in ("换一只猫娘", "换个形象") else "first"
        ok, msg, img = self.catgirl.finalize_adoption(gid, uid, choice=choice)
        self._pending_adoptions.pop(uid, None)
        yield self._mixed_result(event, msg, img)

    @neko_command("成长档案", alias={"猫娘状态", "猫猫状态", "猫猫档案"}, desc="查看猫娘状态、成长、亲密等级、风险和当前趋势")
    async def catgirl_status(self, event: AstrMessageEvent):
        uid = self._uid(event)
        ok, msg, img_path = self.catgirl.status(uid)
        yield self._mixed_result(event, msg, img_path)

    @neko_command("喂猫", alias={"喂猫娘", "喂猫猫"}, desc="给猫娘喂食，消耗宝石并提升饱食、心情、精力、成长和亲密")
    async def feed_catgirl(self, event: AstrMessageEvent):
        uid = self._uid(event)
        ok, msg, img_path = self.catgirl.feed(uid)
        yield self._mixed_result(event, msg, img_path)

    @neko_command("猫娘打工", alias={"猫猫打工", "打工"}, desc="猫娘打工 [地点名|列表|解锁 地点名]：派猫娘打工、查看地点或解锁地点")
    async def catgirl_work(self, event: AstrMessageEvent, job_name: GreedyStr):
        uid = self._uid(event)
        ok, msg, img = self.catgirl.work(uid, str(job_name or "").strip())
        yield self._mixed_result(event, msg, img)

    @neko_command("猫娘商店", alias={"猫猫商店"}, desc="猫娘商店 [分类]：查看可购买道具和价格")
    async def catgirl_shop(self, event: AstrMessageEvent, category: GreedyStr):
        uid = self._uid(event)
        ok, msg, img = self.catgirl.shop(uid, str(category or "").strip())
        yield self._mixed_result(event, msg, img)

    @neko_command("背包", alias={"猫娘背包", "猫猫背包"}, desc="查看背包道具数量和待生效加成")
    async def catgirl_bag(self, event: AstrMessageEvent):
        uid = self._uid(event)
        ok, msg, img = self.catgirl.bag(uid)
        yield self._mixed_result(event, msg, img)

    @neko_command("购买", alias={"购买道具", "猫娘购买"}, desc="购买 道具名 [数量]：消耗宝石购买商店道具")
    async def catgirl_buy(self, event: AstrMessageEvent, item_name: GreedyStr):
        uid = self._uid(event)
        ok, msg, img = self.catgirl.buy_item(uid, str(item_name or "").strip())
        yield self._mixed_result(event, msg, img)

    @neko_command("使用", alias={"使用道具", "猫娘使用"}, desc="使用 道具名：使用背包道具，功能卡会在对应操作自动消耗")
    async def catgirl_use_item(self, event: AstrMessageEvent, item_name: GreedyStr):
        uid = self._uid(event)
        ok, msg, img = self.catgirl.use_item(uid, str(item_name or "").strip())
        yield self._mixed_result(event, msg, img)

    @neko_command("猫娘护理", alias={"猫猫护理", "护理猫娘", "猫娘看病"}, desc="猫娘护理 [服务名]：查看或购买护理服务")
    async def catgirl_care_service(self, event: AstrMessageEvent, service_name: GreedyStr):
        uid = self._uid(event)
        ok, msg, img = self.catgirl.care_service(uid, str(service_name or "").strip())
        yield self._mixed_result(event, msg, img)

    @neko_command("撸猫", alias={"逗猫", "摸猫", "rua猫", "陪猫娘", "陪猫猫", "贴贴猫娘", "贴贴猫猫"}, desc="进行内置互动，受冷却、精力、心情和每日收益递减影响")
    async def interact_catgirl(self, event: AstrMessageEvent):
        uid = self._uid(event)
        action = (event.message_str or "").strip()
        ok, msg, img = self.catgirl.interact(uid, action)
        yield self._mixed_result(event, msg, img)

    @neko_command("猫娘互动", alias={"猫猫互动"}, desc="猫娘互动 动作名：触发 Pages 中配置的自定义互动")
    async def interact_catgirl_custom(self, event: AstrMessageEvent, action: GreedyStr):
        uid = self._uid(event)
        action = str(action or "").strip()
        if not action:
            yield event.plain_result("请输入要进行的互动动作。")
            return
        ok, msg, img = self.catgirl.interact(uid, action)
        yield self._mixed_result(event, msg, img)

    @neko_command("猫娘改名", desc="猫娘改名 新名字：消耗改名卡修改猫娘名字")
    async def rename_catgirl(self, event: AstrMessageEvent, name: GreedyStr):
        uid = self._uid(event)
        ok, msg, img = self.catgirl.rename(uid, name)
        yield self._mixed_result(event, msg, img)

    @neko_command("更换猫娘形象", alias={"更换猫猫形象"}, desc="更换猫娘形象：上传新图片，优先消耗形象更改卡")
    async def change_catgirl_image(self, event: AstrMessageEvent):

        uid = self._uid(event)
        image_src = self._extract_first_image(event)

        if not self.catgirl.has_catgirl(uid):
            yield event.plain_result("你还没有猫娘喔～发送「请赐我一只可爱猫娘吧」试试看。")
            return

        if not image_src:
            token = f"{time.time()}:{random.random()}"
            self._pending_image_changes[uid] = {"token": token, "expire": time.time() + 120}
            _, _, appearance_price = self._wish_rules()
            yield event.plain_result(f"请在 2 分钟内发送新的猫娘图片～\n成功更换时会优先消耗 1 张形象更改卡；没有卡时扣除 {appearance_price} {self._coin_name()}。")
            return

        ok, msg, img = await self.catgirl.change_image(uid, image_src)
        yield self._mixed_result(event, msg, img)

    @filter.custom_filter(pending_image_filter(), False)
    async def pending_image_listener(self, event: AstrMessageEvent):
        uid = self._uid(event)
        if uid not in self._pending_image_changes:
            return
        pending = self._pending_image_changes.get(uid)
        if not pending:
            return
        if time.time() > float(pending.get("expire", 0)):
            self._pending_image_changes.pop(uid, None)
            return

        image_src = self._extract_first_image(event)
        if not image_src:
            return

        self._pending_image_changes.pop(uid, None)
        ok, msg, img = await self.catgirl.change_image(uid, image_src)
        yield self._mixed_result(event, msg, img)


    @neko_command("羁绊排行榜", alias={"猫娘排行榜", "猫猫排行榜"}, desc="查看当前群猫娘羁绊排行榜")
    async def catgirl_rank(self, event: AstrMessageEvent):
        gid = self._gid(event)
        img = self.catgirl.draw_rank(gid)
        if not img:
            yield event.plain_result("本群还没有登记猫娘喔～发送「请赐我一只可爱猫娘吧」试试看。")
            return
        yield event.image_result(str(img))

    @neko_command("迁移猫娘到本群", alias={"猫娘迁移"}, desc="把自己的猫娘登记到当前群排行榜")
    async def migrate_catgirl_to_group(self, event: AstrMessageEvent):
        uid = self._uid(event)
        gid = self._gid(event)
        ok, msg, img = self.catgirl.migrate_to_group(gid, uid)
        yield self._mixed_result(event, msg, img)

    @neko_command("钱包排行榜", desc="查看宝石余额排行榜")
    async def wallet_rank(self, event: AstrMessageEvent):
        rows = self.economy.wallet_rank(10)
        if not rows:
            yield event.plain_result("还没有人有钱钱喔～")
            return
        coin_name = self._coin_name()
        lines = [f"💰 {coin_name}排行榜 TOP 10\n"]
        for i, row in enumerate(rows, 1):
            lines.append(f"{i}. {row['uid']}: {row['balance']} {coin_name}")
        yield event.plain_result("\n".join(lines))

    @neko_command("管理员给", desc="管理员给 数量 @用户：给指定用户增加宝石")
    async def admin_give(self, event: AstrMessageEvent, amount: int):
        if not self._is_admin(event):
            return
        if amount <= 0:
            yield event.plain_result("金额要大于 0。")
            return
        target = self._extract_at_uid(event)
        if not target:
            yield event.plain_result("要 @ 目标用户喔～")
            return
        self.economy.add_balance(target, amount)
        yield event.plain_result(f"已给 {target} 添加 {amount} {self._coin_name()}。")

    @neko_command("管理员扣", desc="管理员扣 数量 @用户：扣除指定用户宝石")
    async def admin_deduct(self, event: AstrMessageEvent, amount: int):
        if not self._is_admin(event):
            return
        if amount <= 0:
            yield event.plain_result("金额要大于 0。")
            return
        target = self._extract_at_uid(event)
        if not target:
            yield event.plain_result("要 @ 目标用户喔～")
            return
        self.economy.add_balance(target, -amount)
        yield event.plain_result(f"已从 {target} 扣除 {amount} {self._coin_name()}。")

    @neko_command("管理员查看", desc="管理员查看 @用户：查看指定用户宝石余额")
    async def admin_check(self, event: AstrMessageEvent):
        if not self._is_admin(event):
            return
        target = self._extract_at_uid(event)
        if not target:
            yield event.plain_result("要 @ 目标用户喔～")
            return
        bal = self.economy.get_balance(target)
        yield event.plain_result(f"用户 {target} 当前余额：{bal} {self._coin_name()}")
