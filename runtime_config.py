import copy
import json
import re
import time
from pathlib import Path
from typing import Any, Dict


def default_runtime_config() -> Dict[str, Any]:
    return {
        "version": 1,
        "economy": {
            "coin_name": "宝石",
            "sign_min_reward": 65,
            "sign_max_reward": 125,
            "daily_work_min_reward": 35,
            "daily_work_max_reward": 85,
            "daily_work_events": [
                "你在猫咖帮忙端了一天甜点。",
                "你帮老板整理仓库，累得耳朵都耷拉下来了。",
                "你接了一个临时外包，顺利完成。",
                "你在便利店值班，遇到了一群买关东煮的猫娘。",
                "你帮别人修好了坏掉的自动贩卖机。",
                "你去花店帮忙包花，顺手学会了新的蝴蝶结打法。",
                "你在图书馆整理书架，被安静的午后治愈了一点。",
                "你给游戏展台做临时引导，嗓子有点哑但赚到了奖金。",
                "你帮甜品师试吃新品，认真写下了口味反馈。",
                "你接了外卖跑腿任务，绕了半座城才赶上时间。",
                "你在水族馆做导览，给小朋友介绍了发呆的海豹。",
                "你帮摄影棚布置场景，灯光调好时整间屋子都亮了。",
                "你去手作市集看摊，卖出了一排猫爪挂件。",
                "你替邻居照看盆栽，意外收到一份感谢红包。",
                "你在夜市帮摊主收摊，带回了热乎乎的宵夜。",
            ],
        },
        "wish": {
            "probability": 0.8,
            "pity": 3,
            "appearance_change_price": 900,
        },
        "care": {
            "feed_satiety_limit": 85,
            "satiety_decay_minutes": 2880,
            "mood_decay_per_day": 4,
            "energy_recovery_per_day": 32,
            "health_hungry_decay_per_day": 6,
            "health_low_mood_decay_per_day": 3,
            "health_recovery_per_day": 1.5,
            "health_hungry_satiety_threshold": 20,
            "health_low_mood_threshold": 30,
            "runaway_after_zero_hours": 168,
            "interaction_daily_limit": 5,
            "interaction_cooldown_seconds": 300,
            "interaction_energy_cost": 4,
            "interaction_soft_limit_extra": 3,
            "interaction_heavy_limit_extra": 7,
            "interaction_soft_limit_multiplier": 0.65,
            "interaction_heavy_limit_multiplier": 0.35,
            "interaction_minimal_limit_multiplier": 0.15,
            "interaction_good_mood_threshold": 80,
            "interaction_low_mood_threshold": 50,
            "interaction_bad_mood_threshold": 30,
            "interaction_high_mood_multiplier": 1.12,
            "interaction_low_mood_multiplier": 0.8,
            "interaction_bad_mood_multiplier": 0.55,
            "feed_healthy_threshold": 70,
            "feed_low_health_threshold": 40,
            "feed_bad_health_threshold": 20,
            "feed_low_health_multiplier": 0.9,
            "feed_bad_health_multiplier": 0.72,
            "feed_critical_health_multiplier": 0.55,
            "work_stable_energy_threshold": 55,
            "work_high_energy_threshold": 85,
            "work_stable_energy_reward_multiplier": 1.04,
            "work_high_energy_reward_multiplier": 1.12,
            "work_min_health": 35,
            "interact_min_health": 20,
            "work_min_satiety": 20,
            "work_min_mood": 30,
        },
        "personalities": {
            "effects": [
                {
                    "name": "害羞",
                    "satiety_decay_multiplier": 1,
                    "mood_decay_multiplier": 1,
                    "energy_recovery_multiplier": 1,
                    "health_recovery_multiplier": 1,
                    "feed_satiety_multiplier": 1,
                    "feed_mood_multiplier": 1,
                    "feed_growth_multiplier": 1,
                    "feed_intimacy_multiplier": 1,
                    "work_reward_multiplier": 1,
                    "work_energy_cost_multiplier": 1,
                    "work_growth_multiplier": 1,
                    "work_intimacy_multiplier": 1,
                    "interaction_mood_multiplier": 1,
                    "interaction_growth_multiplier": 1,
                    "interaction_intimacy_multiplier": 1.15,
                    "interaction_energy_cost_multiplier": 1,
                    "enabled": True,
                },
                {
                    "name": "活泼",
                    "satiety_decay_multiplier": 1.05,
                    "mood_decay_multiplier": 1,
                    "energy_recovery_multiplier": 1.12,
                    "health_recovery_multiplier": 1,
                    "feed_satiety_multiplier": 1,
                    "feed_mood_multiplier": 1.08,
                    "feed_growth_multiplier": 1,
                    "feed_intimacy_multiplier": 1,
                    "work_reward_multiplier": 1,
                    "work_energy_cost_multiplier": 1.08,
                    "work_growth_multiplier": 1.08,
                    "work_intimacy_multiplier": 1,
                    "interaction_mood_multiplier": 1.12,
                    "interaction_growth_multiplier": 1.12,
                    "interaction_intimacy_multiplier": 1,
                    "interaction_energy_cost_multiplier": 1.05,
                    "enabled": True,
                },
                {
                    "name": "傲娇",
                    "satiety_decay_multiplier": 1,
                    "mood_decay_multiplier": 1.08,
                    "energy_recovery_multiplier": 1,
                    "health_recovery_multiplier": 1,
                    "feed_satiety_multiplier": 1,
                    "feed_mood_multiplier": 0.95,
                    "feed_growth_multiplier": 1.05,
                    "feed_intimacy_multiplier": 0.95,
                    "work_reward_multiplier": 1.05,
                    "work_energy_cost_multiplier": 1,
                    "work_growth_multiplier": 1.05,
                    "work_intimacy_multiplier": 0.95,
                    "interaction_mood_multiplier": 0.95,
                    "interaction_growth_multiplier": 1.05,
                    "interaction_intimacy_multiplier": 0.95,
                    "interaction_energy_cost_multiplier": 1,
                    "enabled": True,
                },
                {
                    "name": "温柔",
                    "satiety_decay_multiplier": 1,
                    "mood_decay_multiplier": 0.95,
                    "energy_recovery_multiplier": 1,
                    "health_recovery_multiplier": 1.15,
                    "feed_satiety_multiplier": 1,
                    "feed_mood_multiplier": 1.05,
                    "feed_growth_multiplier": 1,
                    "feed_intimacy_multiplier": 1.05,
                    "work_reward_multiplier": 1,
                    "work_energy_cost_multiplier": 1,
                    "work_growth_multiplier": 1,
                    "work_intimacy_multiplier": 1.05,
                    "interaction_mood_multiplier": 1.08,
                    "interaction_growth_multiplier": 1,
                    "interaction_intimacy_multiplier": 1.08,
                    "interaction_energy_cost_multiplier": 1,
                    "enabled": True,
                },
                {
                    "name": "贪吃",
                    "satiety_decay_multiplier": 1.15,
                    "mood_decay_multiplier": 1,
                    "energy_recovery_multiplier": 1,
                    "health_recovery_multiplier": 1,
                    "feed_satiety_multiplier": 1.2,
                    "feed_mood_multiplier": 1.12,
                    "feed_growth_multiplier": 1,
                    "feed_intimacy_multiplier": 1,
                    "work_reward_multiplier": 1,
                    "work_energy_cost_multiplier": 1,
                    "work_growth_multiplier": 1,
                    "work_intimacy_multiplier": 1,
                    "interaction_mood_multiplier": 1,
                    "interaction_growth_multiplier": 1,
                    "interaction_intimacy_multiplier": 1,
                    "interaction_energy_cost_multiplier": 1,
                    "enabled": True,
                },
                {
                    "name": "慵懒",
                    "satiety_decay_multiplier": 0.95,
                    "mood_decay_multiplier": 0.92,
                    "energy_recovery_multiplier": 1.15,
                    "health_recovery_multiplier": 1,
                    "feed_satiety_multiplier": 1,
                    "feed_mood_multiplier": 1,
                    "feed_growth_multiplier": 0.95,
                    "feed_intimacy_multiplier": 1,
                    "work_reward_multiplier": 0.92,
                    "work_energy_cost_multiplier": 0.85,
                    "work_growth_multiplier": 0.95,
                    "work_intimacy_multiplier": 1,
                    "interaction_mood_multiplier": 1,
                    "interaction_growth_multiplier": 0.95,
                    "interaction_intimacy_multiplier": 1.05,
                    "interaction_energy_cost_multiplier": 0.9,
                    "enabled": True,
                },
                {
                    "name": "认真",
                    "satiety_decay_multiplier": 1,
                    "mood_decay_multiplier": 1,
                    "energy_recovery_multiplier": 0.98,
                    "health_recovery_multiplier": 1,
                    "feed_satiety_multiplier": 1,
                    "feed_mood_multiplier": 1,
                    "feed_growth_multiplier": 1.1,
                    "feed_intimacy_multiplier": 1,
                    "work_reward_multiplier": 1.15,
                    "work_energy_cost_multiplier": 1.05,
                    "work_growth_multiplier": 1.12,
                    "work_intimacy_multiplier": 1,
                    "interaction_mood_multiplier": 1,
                    "interaction_growth_multiplier": 1.08,
                    "interaction_intimacy_multiplier": 1,
                    "interaction_energy_cost_multiplier": 1,
                    "enabled": True,
                },
                {
                    "name": "黏人",
                    "satiety_decay_multiplier": 1,
                    "mood_decay_multiplier": 0.9,
                    "energy_recovery_multiplier": 1,
                    "health_recovery_multiplier": 1,
                    "feed_satiety_multiplier": 1,
                    "feed_mood_multiplier": 1.05,
                    "feed_growth_multiplier": 1,
                    "feed_intimacy_multiplier": 1.12,
                    "work_reward_multiplier": 1,
                    "work_energy_cost_multiplier": 1,
                    "work_growth_multiplier": 1,
                    "work_intimacy_multiplier": 1.1,
                    "interaction_mood_multiplier": 1.05,
                    "interaction_growth_multiplier": 1,
                    "interaction_intimacy_multiplier": 1.2,
                    "interaction_energy_cost_multiplier": 1,
                    "enabled": True,
                },
            ],
        },
        "feed": {
            "satiety_add_min": 18,
            "satiety_add_max": 30,
            "mood_add_min": 2,
            "mood_add_max": 7,
            "health_add_min": 0,
            "health_add_max": 3,
            "energy_add_min": 4,
            "energy_add_max": 9,
            "growth_add_min": 3,
            "growth_add_max": 7,
            "intimacy_add_min": 1,
            "intimacy_add_max": 3,
            "foods": [
                {"name": "草莓奶油蛋糕", "cost_min": 32, "cost_max": 58, "verb": "吃", "enabled": True},
                {"name": "热乎乎的蛋包饭", "cost_min": 30, "cost_max": 52, "verb": "吃", "enabled": True},
                {"name": "芝士焗饭", "cost_min": 38, "cost_max": 68, "verb": "吃", "enabled": True},
                {"name": "炸鸡块", "cost_min": 24, "cost_max": 44, "verb": "吃", "enabled": True},
                {"name": "牛奶布丁", "cost_min": 18, "cost_max": 32, "verb": "吃", "enabled": True},
                {"name": "珍珠奶茶", "cost_min": 20, "cost_max": 38, "verb": "喝", "enabled": True},
                {"name": "抹茶拿铁", "cost_min": 22, "cost_max": 42, "verb": "喝", "enabled": True},
                {"name": "可颂面包", "cost_min": 18, "cost_max": 34, "verb": "吃", "enabled": True},
                {"name": "巧克力曲奇", "cost_min": 16, "cost_max": 30, "verb": "吃", "enabled": True},
                {"name": "海鲜乌冬面", "cost_min": 45, "cost_max": 78, "verb": "吃", "enabled": True},
                {"name": "小鱼干便当", "cost_min": 34, "cost_max": 60, "verb": "吃", "enabled": True},
                {"name": "奶油蘑菇汤", "cost_min": 24, "cost_max": 42, "verb": "喝", "enabled": True},
                {"name": "鲷鱼烧", "cost_min": 22, "cost_max": 40, "verb": "吃", "enabled": True},
                {"name": "三文鱼茶泡饭", "cost_min": 46, "cost_max": 82, "verb": "吃", "enabled": True},
                {"name": "猫爪棉花糖", "cost_min": 18, "cost_max": 34, "verb": "吃", "enabled": True},
                {"name": "蜂蜜厚松饼", "cost_min": 34, "cost_max": 60, "verb": "吃", "enabled": True},
                {"name": "关东煮", "cost_min": 26, "cost_max": 46, "verb": "吃", "enabled": True},
                {"name": "海盐焦糖拿铁", "cost_min": 24, "cost_max": 44, "verb": "喝", "enabled": True},
                {"name": "莓果酸奶杯", "cost_min": 22, "cost_max": 40, "verb": "吃", "enabled": True},
                {"name": "蟹肉可乐饼", "cost_min": 36, "cost_max": 64, "verb": "吃", "enabled": True},
                {"name": "玉子烧便当", "cost_min": 32, "cost_max": 56, "verb": "吃", "enabled": True},
                {"name": "南瓜浓汤", "cost_min": 22, "cost_max": 40, "verb": "喝", "enabled": True},
                {"name": "抹茶红豆大福", "cost_min": 26, "cost_max": 48, "verb": "吃", "enabled": True},
                {"name": "烤饭团", "cost_min": 22, "cost_max": 38, "verb": "吃", "enabled": True},
            ],
        },
        "work": {
            "reward_stage_base": 0.75,
            "reward_stage_step": 0.10,
            "jobs": [
                {"id": "cat_cafe", "name": "猫咖服务员", "reward_min": 80, "reward_max": 150, "duration_minutes": 45, "energy_cost": 18, "satiety_cost": 7, "mood_cost": 2, "growth_min": 4, "growth_max": 7, "intimacy_min": 1, "intimacy_max": 2, "mood_reward": 1, "unlock_cost": 0, "min_stage": 0, "enabled": True},
                {"id": "dessert_shop", "name": "甜点店看板娘", "reward_min": 90, "reward_max": 165, "duration_minutes": 60, "energy_cost": 22, "satiety_cost": 8, "mood_cost": 2, "growth_min": 5, "growth_max": 8, "intimacy_min": 1, "intimacy_max": 3, "mood_reward": 1, "unlock_cost": 0, "min_stage": 0, "enabled": True},
                {"id": "night_store", "name": "便利店夜班", "reward_min": 140, "reward_max": 260, "duration_minutes": 120, "energy_cost": 40, "satiety_cost": 15, "mood_cost": 7, "growth_min": 9, "growth_max": 15, "intimacy_min": 2, "intimacy_max": 5, "mood_reward": 1, "unlock_cost": 900, "min_stage": 1, "enabled": True},
                {"id": "doujin_booth", "name": "同人展摊位助手", "reward_min": 175, "reward_max": 330, "duration_minutes": 180, "energy_cost": 52, "satiety_cost": 19, "mood_cost": 9, "growth_min": 12, "growth_max": 21, "intimacy_min": 3, "intimacy_max": 7, "mood_reward": 1, "unlock_cost": 1800, "min_stage": 2, "enabled": True},
                {"id": "milk_tea", "name": "奶茶店试喝员", "reward_min": 65, "reward_max": 120, "duration_minutes": 30, "energy_cost": 14, "satiety_cost": 5, "mood_cost": 1, "growth_min": 3, "growth_max": 5, "intimacy_min": 1, "intimacy_max": 2, "mood_reward": 1, "unlock_cost": 0, "min_stage": 0, "enabled": True},
                {"id": "library_helper", "name": "图书馆整理员", "reward_min": 75, "reward_max": 140, "duration_minutes": 50, "energy_cost": 17, "satiety_cost": 6, "mood_cost": 1, "growth_min": 4, "growth_max": 7, "intimacy_min": 1, "intimacy_max": 2, "mood_reward": 1, "unlock_cost": 0, "min_stage": 0, "enabled": True},
                {"id": "flower_shop", "name": "花店临时助手", "reward_min": 95, "reward_max": 175, "duration_minutes": 55, "energy_cost": 21, "satiety_cost": 8, "mood_cost": 1, "growth_min": 5, "growth_max": 9, "intimacy_min": 1, "intimacy_max": 3, "mood_reward": 1, "unlock_cost": 0, "min_stage": 0, "enabled": True},
                {"id": "game_booth", "name": "游戏展台助理", "reward_min": 120, "reward_max": 220, "duration_minutes": 90, "energy_cost": 32, "satiety_cost": 11, "mood_cost": 4, "growth_min": 7, "growth_max": 12, "intimacy_min": 2, "intimacy_max": 4, "mood_reward": 1, "unlock_cost": 650, "min_stage": 1, "enabled": True},
                {"id": "pet_hospital", "name": "宠物医院前台", "reward_min": 130, "reward_max": 240, "duration_minutes": 100, "energy_cost": 35, "satiety_cost": 12, "mood_cost": 4, "growth_min": 8, "growth_max": 13, "intimacy_min": 2, "intimacy_max": 5, "mood_reward": 1, "unlock_cost": 850, "min_stage": 1, "enabled": True},
                {"id": "aquarium_guide", "name": "水族馆导览员", "reward_min": 170, "reward_max": 310, "duration_minutes": 150, "energy_cost": 46, "satiety_cost": 16, "mood_cost": 6, "growth_min": 11, "growth_max": 19, "intimacy_min": 3, "intimacy_max": 6, "mood_reward": 1, "unlock_cost": 1600, "min_stage": 2, "enabled": True},
                {"id": "handmade_market", "name": "手作市集看摊", "reward_min": 160, "reward_max": 290, "duration_minutes": 150, "energy_cost": 43, "satiety_cost": 15, "mood_cost": 5, "growth_min": 10, "growth_max": 17, "intimacy_min": 3, "intimacy_max": 6, "mood_reward": 1, "unlock_cost": 1400, "min_stage": 2, "enabled": True},
                {"id": "photo_studio", "name": "摄影棚布景助手", "reward_min": 210, "reward_max": 380, "duration_minutes": 180, "energy_cost": 55, "satiety_cost": 19, "mood_cost": 7, "growth_min": 13, "growth_max": 23, "intimacy_min": 4, "intimacy_max": 8, "mood_reward": 1, "unlock_cost": 2800, "min_stage": 3, "enabled": True},
                {"id": "star_train_attendant", "name": "星轨列车乘务员", "reward_min": 280, "reward_max": 500, "duration_minutes": 240, "energy_cost": 66, "satiety_cost": 24, "mood_cost": 9, "growth_min": 18, "growth_max": 32, "intimacy_min": 5, "intimacy_max": 10, "mood_reward": 1, "unlock_cost": 4800, "min_stage": 4, "enabled": True},
            ],
        },
        "shop": {
            "gift_daily_limit": 5,
            "gift_soft_limit_extra": 5,
            "gift_soft_limit_multiplier": 0.5,
            "gift_minimal_limit_multiplier": 0.2,
            "items": [
                {"id": "dried_fish_gift", "name": "小鱼干礼盒", "category": "礼物", "price": 90, "description": "亲密和心情小幅提升。", "effect": "gift", "mood_min": 2, "mood_max": 4, "intimacy_min": 1, "intimacy_max": 2, "growth_min": 0, "growth_max": 1, "enabled": True},
                {"id": "ribbon_hairpin", "name": "丝带发夹", "category": "礼物", "price": 220, "description": "亲密提升，并获得少量成长。", "effect": "gift", "mood_min": 2, "mood_max": 5, "intimacy_min": 2, "intimacy_max": 4, "growth_min": 1, "growth_max": 2, "enabled": True},
                {"id": "handmade_snack", "name": "手作点心", "category": "礼物", "price": 320, "description": "亲密和心情稳定提升。", "effect": "gift", "mood_min": 4, "mood_max": 8, "intimacy_min": 3, "intimacy_max": 5, "growth_min": 1, "growth_max": 3, "enabled": True},
                {"id": "star_sand_necklace", "name": "星砂项链", "category": "礼物", "price": 900, "description": "昂贵礼物，亲密和成长提升明显。", "effect": "gift", "mood_min": 8, "mood_max": 14, "intimacy_min": 8, "intimacy_max": 12, "growth_min": 4, "growth_max": 8, "weekly_limit": 2, "enabled": True},
                {"id": "cat_teaser", "name": "逗猫棒", "category": "道具", "price": 180, "description": "下一次互动成长和亲密收益提高 20%。", "effect": "next_interaction", "multiplier": 1.2, "enabled": True},
                {"id": "energy_drink", "name": "精力饮品", "category": "护理", "price": 180, "description": "精力 +20，心情 -3。", "effect": "instant", "energy_add": 20, "mood_add": -3, "enabled": True},
                {"id": "nutrition", "name": "营养补剂", "category": "护理", "price": 240, "description": "健康 +10，饱食 +10。", "effect": "instant", "health_add": 10, "satiety_add": 10, "enabled": True},
                {"id": "lucky_badge", "name": "幸运工牌", "category": "道具", "price": 420, "description": "下一次猫娘打工报酬提高 15%。", "effect": "next_work", "multiplier": 1.15, "enabled": True},
                {"id": "premium_bento", "name": "高级便当", "category": "食物", "price": 220, "description": "饱食 +35，心情 +8，健康 +3。", "effect": "instant", "satiety_add": 35, "mood_add": 8, "health_add": 3, "enabled": True},
                {"id": "red_thread_of_fate", "name": "命运的红线", "category": "功能卡", "price": 1200, "description": "召回已经离家出走的猫娘。", "effect": "recall_runaway", "enabled": True},
                {"id": "rename_card", "name": "改名卡", "category": "功能卡", "price": 300, "description": "改名时自动消耗，可免费修改一次猫娘名字。", "effect": "rename_card", "enabled": True},
                {"id": "appearance_card", "name": "形象更改卡", "category": "功能卡", "price": 900, "description": "更换猫娘形象时自动消耗，可免除一次形象更换费用。", "effect": "appearance_card", "enabled": True},
            ],
            "care_services": [
                {"id": "clinic", "name": "看病", "category": "护理", "base_price": 180, "price_per_missing": 4, "target_health": 75, "mood_add": 0, "energy_add": 0, "cooldown_seconds": 21600, "enabled": True},
                {"id": "advanced_clinic", "name": "高级诊疗", "category": "护理", "base_price": 620, "price_per_missing": 8, "target_health": 95, "mood_add": 0, "energy_add": 0, "cooldown_seconds": 86400, "enabled": True},
                {"id": "rest_package", "name": "休息套餐", "category": "护理", "base_price": 150, "price_per_missing": 0, "target_health": 0, "mood_add": 6, "energy_add": 28, "cooldown_seconds": 28800, "enabled": True},
                {"id": "massage", "name": "按摩护理", "category": "护理", "base_price": 240, "price_per_missing": 0, "target_health": 0, "mood_add": 16, "energy_add": 8, "cooldown_seconds": 28800, "enabled": True},
                {"id": "onsen", "name": "温泉放松", "category": "护理", "base_price": 650, "price_per_missing": 0, "target_health": 0, "health_add": 10, "mood_add": 25, "energy_add": 16, "cooldown_seconds": 86400, "enabled": True},
            ],
        },
        "interactions": {
            "effects": [
                {"command": "撸猫", "text": "你轻轻撸了撸她的头发，她舒服地眯起眼睛。", "mood_min": 5, "mood_max": 10, "intimacy_min": 2, "intimacy_max": 4, "growth_min": 2, "growth_max": 4, "energy_cost": 0, "min_stage": 0, "enabled": True},
                {"command": "逗猫", "text": "你拿出小玩具逗她，她开心地扑来扑去。", "mood_min": 7, "mood_max": 13, "intimacy_min": 2, "intimacy_max": 4, "growth_min": 3, "growth_max": 5, "energy_cost": 6, "min_stage": 0, "enabled": True},
                {"command": "摸猫", "text": "你摸了摸她的脑袋，她小声地喵了一下。", "mood_min": 4, "mood_max": 9, "intimacy_min": 2, "intimacy_max": 5, "growth_min": 2, "growth_max": 4, "energy_cost": 0, "min_stage": 0, "enabled": True},
                {"command": "rua猫", "text": "你把她 rua 成了一团软乎乎的猫猫球。", "mood_min": 5, "mood_max": 10, "intimacy_min": 3, "intimacy_max": 6, "growth_min": 2, "growth_max": 4, "energy_cost": 2, "min_stage": 0, "enabled": True},
                {"command": "陪猫娘", "text": "你陪她聊了一会儿，她看起来安心了很多。", "mood_min": 4, "mood_max": 8, "intimacy_min": 4, "intimacy_max": 8, "growth_min": 2, "growth_max": 5, "energy_cost": 0, "min_stage": 0, "enabled": True},
                {"command": "陪猫猫", "text": "你陪她窝在一起晒太阳，气氛软绵绵的。", "mood_min": 4, "mood_max": 8, "intimacy_min": 4, "intimacy_max": 8, "growth_min": 2, "growth_max": 5, "energy_cost": 0, "min_stage": 0, "enabled": True},
                {"command": "贴贴猫娘", "text": "你和她贴贴了一下，她脸红地别过头。", "mood_min": 4, "mood_max": 8, "intimacy_min": 5, "intimacy_max": 10, "growth_min": 3, "growth_max": 6, "energy_cost": 0, "min_stage": 2, "enabled": True},
                {"command": "贴贴猫猫", "text": "你和她贴贴了一下，她尾巴轻轻晃了晃。", "mood_min": 4, "mood_max": 8, "intimacy_min": 5, "intimacy_max": 10, "growth_min": 3, "growth_max": 6, "energy_cost": 0, "min_stage": 2, "enabled": True},
            ],
        },
    }


class NekoRuntimeConfig:
    def __init__(self, path: Path, legacy_config: Dict[str, Any] | None = None):
        self.path = Path(path)
        self.data = default_runtime_config()
        first_boot = not self.path.exists()
        self.load()
        if first_boot and legacy_config:
            self.data = self.normalize(self._with_legacy_config(self.data, legacy_config))
            self.save()

    def load(self) -> Dict[str, Any]:
        if self.path.exists():
            try:
                with self.path.open("r", encoding="utf-8") as f:
                    raw = json.load(f)
                self.data = self.normalize(raw)
            except Exception:
                self.data = default_runtime_config()
        else:
            self.data = default_runtime_config()
            self.save()
        return self.snapshot()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        tmp.replace(self.path)

    def snapshot(self) -> Dict[str, Any]:
        return copy.deepcopy(self.data)

    def replace(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.data = self.normalize(payload)
        self.save()
        return self.snapshot()

    def reset(self) -> Dict[str, Any]:
        self.data = default_runtime_config()
        self.save()
        return self.snapshot()

    def normalize(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        base = default_runtime_config()
        src = payload if isinstance(payload, dict) else {}

        economy = src.get("economy") if isinstance(src.get("economy"), dict) else {}
        base["economy"].update({
            "coin_name": self._text(economy.get("coin_name"), "宝石", 16),
            "sign_min_reward": self._int(economy.get("sign_min_reward"), 65, 0, 1_000_000),
            "sign_max_reward": self._int(economy.get("sign_max_reward"), 125, 0, 1_000_000),
            "daily_work_min_reward": self._int(economy.get("daily_work_min_reward"), 35, 0, 1_000_000),
            "daily_work_max_reward": self._int(economy.get("daily_work_max_reward"), 85, 0, 1_000_000),
            "daily_work_events": self._text_list(economy.get("daily_work_events"), base["economy"]["daily_work_events"], 80, 20),
        })
        self._ensure_order(base["economy"], "sign_min_reward", "sign_max_reward")
        self._ensure_order(base["economy"], "daily_work_min_reward", "daily_work_max_reward")

        wish = src.get("wish") if isinstance(src.get("wish"), dict) else {}
        base["wish"].update({
            "probability": self._float(wish.get("probability"), 0.8, 0, 1),
            "pity": self._int(wish.get("pity"), 3, 1, 365),
            "appearance_change_price": self._int(wish.get("appearance_change_price"), 900, 0, 1_000_000),
        })

        care = src.get("care") if isinstance(src.get("care"), dict) else {}
        for key, default, low, high in [
            ("feed_satiety_limit", 85, 0, 100),
            ("satiety_decay_minutes", 2880, 1, 100_000),
            ("mood_decay_per_day", 4, 0, 1000),
            ("energy_recovery_per_day", 32, 0, 1000),
            ("health_hungry_decay_per_day", 6, 0, 1000),
            ("health_low_mood_decay_per_day", 3, 0, 1000),
            ("health_recovery_per_day", 1.5, 0, 1000),
            ("health_hungry_satiety_threshold", 20, 0, 100),
            ("health_low_mood_threshold", 30, 0, 100),
            ("runaway_after_zero_hours", 168, 1, 10_000),
            ("interaction_daily_limit", 5, 0, 1000),
            ("interaction_cooldown_seconds", 300, 0, 86_400),
            ("interaction_energy_cost", 4, 0, 100),
            ("interaction_soft_limit_extra", 3, 0, 1000),
            ("interaction_heavy_limit_extra", 7, 0, 1000),
            ("interaction_soft_limit_multiplier", 0.65, 0, 10),
            ("interaction_heavy_limit_multiplier", 0.35, 0, 10),
            ("interaction_minimal_limit_multiplier", 0.15, 0, 10),
            ("interaction_good_mood_threshold", 80, 0, 100),
            ("interaction_low_mood_threshold", 50, 0, 100),
            ("interaction_bad_mood_threshold", 30, 0, 100),
            ("interaction_high_mood_multiplier", 1.12, 0, 10),
            ("interaction_low_mood_multiplier", 0.8, 0, 10),
            ("interaction_bad_mood_multiplier", 0.55, 0, 10),
            ("feed_healthy_threshold", 70, 0, 100),
            ("feed_low_health_threshold", 40, 0, 100),
            ("feed_bad_health_threshold", 20, 0, 100),
            ("feed_low_health_multiplier", 0.9, 0, 10),
            ("feed_bad_health_multiplier", 0.72, 0, 10),
            ("feed_critical_health_multiplier", 0.55, 0, 10),
            ("work_stable_energy_threshold", 55, 0, 100),
            ("work_high_energy_threshold", 85, 0, 100),
            ("work_stable_energy_reward_multiplier", 1.04, 0, 10),
            ("work_high_energy_reward_multiplier", 1.12, 0, 10),
            ("work_min_health", 35, 0, 100),
            ("interact_min_health", 20, 0, 100),
            ("work_min_satiety", 20, 0, 100),
            ("work_min_mood", 30, 0, 100),
        ]:
            base["care"][key] = self._float(care.get(key), default, low, high)
        base["care"]["interaction_daily_limit"] = int(base["care"]["interaction_daily_limit"])
        for key in ["interaction_cooldown_seconds", "interaction_energy_cost", "interaction_soft_limit_extra", "interaction_heavy_limit_extra"]:
            base["care"][key] = int(base["care"][key])
        if base["care"]["interaction_heavy_limit_extra"] < base["care"]["interaction_soft_limit_extra"]:
            base["care"]["interaction_heavy_limit_extra"] = base["care"]["interaction_soft_limit_extra"]
        if base["care"]["interaction_low_mood_threshold"] < base["care"]["interaction_bad_mood_threshold"]:
            base["care"]["interaction_low_mood_threshold"] = base["care"]["interaction_bad_mood_threshold"]
        if base["care"]["interaction_good_mood_threshold"] < base["care"]["interaction_low_mood_threshold"]:
            base["care"]["interaction_good_mood_threshold"] = base["care"]["interaction_low_mood_threshold"]
        if base["care"]["feed_low_health_threshold"] < base["care"]["feed_bad_health_threshold"]:
            base["care"]["feed_low_health_threshold"] = base["care"]["feed_bad_health_threshold"]
        if base["care"]["feed_healthy_threshold"] < base["care"]["feed_low_health_threshold"]:
            base["care"]["feed_healthy_threshold"] = base["care"]["feed_low_health_threshold"]
        if base["care"]["work_high_energy_threshold"] < base["care"]["work_stable_energy_threshold"]:
            base["care"]["work_high_energy_threshold"] = base["care"]["work_stable_energy_threshold"]

        feed = src.get("feed") if isinstance(src.get("feed"), dict) else {}
        for key, default, low, high in [
            ("satiety_add_min", 18, 0, 100),
            ("satiety_add_max", 30, 0, 100),
            ("mood_add_min", 2, 0, 100),
            ("mood_add_max", 7, 0, 100),
            ("health_add_min", 0, 0, 100),
            ("health_add_max", 3, 0, 100),
            ("energy_add_min", 4, 0, 100),
            ("energy_add_max", 9, 0, 100),
            ("growth_add_min", 3, 0, 10000),
            ("growth_add_max", 7, 0, 10000),
            ("intimacy_add_min", 1, 0, 10000),
            ("intimacy_add_max", 3, 0, 10000),
        ]:
            base["feed"][key] = self._int(feed.get(key), default, low, high)
        for a, b in [
            ("satiety_add_min", "satiety_add_max"),
            ("mood_add_min", "mood_add_max"),
            ("health_add_min", "health_add_max"),
            ("energy_add_min", "energy_add_max"),
            ("growth_add_min", "growth_add_max"),
            ("intimacy_add_min", "intimacy_add_max"),
        ]:
            self._ensure_order(base["feed"], a, b)
        base["feed"]["foods"] = self._foods(feed.get("foods"), base["feed"]["foods"])

        work = src.get("work") if isinstance(src.get("work"), dict) else {}
        for key, default, low, high in [
            ("reward_stage_base", 0.75, 0, 10),
            ("reward_stage_step", 0.10, 0, 10),
        ]:
            base["work"][key] = self._float(work.get(key), default, low, high)
        base["work"]["jobs"] = self._jobs(work.get("jobs"), base["work"]["jobs"])

        shop = src.get("shop") if isinstance(src.get("shop"), dict) else {}
        for key, default, low, high in [
            ("gift_daily_limit", 5, 0, 1000),
            ("gift_soft_limit_extra", 5, 0, 1000),
            ("gift_soft_limit_multiplier", 0.5, 0, 10),
            ("gift_minimal_limit_multiplier", 0.2, 0, 10),
        ]:
            base["shop"][key] = self._float(shop.get(key), default, low, high)
        for key in ["gift_daily_limit", "gift_soft_limit_extra"]:
            base["shop"][key] = int(base["shop"][key])
        base["shop"]["items"] = self._shop_items(shop.get("items"), base["shop"]["items"])
        base["shop"]["care_services"] = self._care_services(shop.get("care_services"), base["shop"]["care_services"])

        personalities = src.get("personalities") if isinstance(src.get("personalities"), dict) else {}
        base["personalities"]["effects"] = self._personalities(
            personalities.get("effects"),
            base["personalities"]["effects"],
        )

        interactions = src.get("interactions") if isinstance(src.get("interactions"), dict) else {}
        base["interactions"]["effects"] = self._interactions(interactions.get("effects"), base["interactions"]["effects"])
        return base

    def _with_legacy_config(self, config: Dict[str, Any], legacy_config: Dict[str, Any]) -> Dict[str, Any]:
        merged = copy.deepcopy(config)
        if not isinstance(legacy_config, dict):
            return merged

        economy = merged.setdefault("economy", {})
        legacy_map = {
            "coin_name": "coin_name",
            "sign_min_reward": "sign_min_reward",
            "sign_max_reward": "sign_max_reward",
            "work_min_reward": "daily_work_min_reward",
            "work_max_reward": "daily_work_max_reward",
        }
        for old_key, new_key in legacy_map.items():
            if old_key in legacy_config:
                economy[new_key] = legacy_config.get(old_key)

        wish = merged.setdefault("wish", {})
        if "catgirl_wish_probability" in legacy_config:
            wish["probability"] = legacy_config.get("catgirl_wish_probability")
        if "catgirl_wish_pity" in legacy_config:
            wish["pity"] = legacy_config.get("catgirl_wish_pity")
        if "appearance_change_price" in legacy_config:
            wish["appearance_change_price"] = legacy_config.get("appearance_change_price")

        return merged

    def _foods(self, rows, defaults):
        result = []
        for row in rows if isinstance(rows, list) else defaults:
            if not isinstance(row, dict):
                continue
            item = {
                "name": self._text(row.get("name"), "食物", 30),
                "cost_min": self._int(row.get("cost_min"), 1, 0, 1_000_000),
                "cost_max": self._int(row.get("cost_max"), 1, 0, 1_000_000),
                "verb": self._text(row.get("verb"), "吃", 8),
                "enabled": bool(row.get("enabled", True)),
            }
            self._ensure_order(item, "cost_min", "cost_max")
            result.append(item)
        return result or copy.deepcopy(defaults)

    def _jobs(self, rows, defaults):
        result = []
        seen = set()
        for row in rows if isinstance(rows, list) else defaults:
            if not isinstance(row, dict):
                continue
            name = self._text(row.get("name"), "打工地点", 40)
            job_id = self._id(row.get("id"), name, seen)
            item = {
                "id": job_id,
                "name": name,
                "reward_min": self._int(row.get("reward_min"), 1, 1, 1_000_000),
                "reward_max": self._int(row.get("reward_max"), 1, 1, 1_000_000),
                "duration_minutes": self._int(row.get("duration_minutes"), 30, 1, 100_000),
                "energy_cost": self._int(row.get("energy_cost"), 0, 0, 100),
                "satiety_cost": self._int(row.get("satiety_cost"), 0, 0, 100),
                "mood_cost": self._int(row.get("mood_cost"), 0, 0, 100),
                "growth_min": self._int(row.get("growth_min"), 0, 0, 100_000),
                "growth_max": self._int(row.get("growth_max"), 0, 0, 100_000),
                "intimacy_min": self._int(row.get("intimacy_min"), 0, 0, 100_000),
                "intimacy_max": self._int(row.get("intimacy_max"), 0, 0, 100_000),
                "mood_reward": self._float(row.get("mood_reward"), 1, 0, 100),
                "unlock_cost": self._int(row.get("unlock_cost"), 0, 0, 1_000_000_000),
                "min_stage": self._int(row.get("min_stage"), 0, 0, 6),
                "enabled": bool(row.get("enabled", True)),
            }
            for a, b in [("reward_min", "reward_max"), ("growth_min", "growth_max"), ("intimacy_min", "intimacy_max")]:
                self._ensure_order(item, a, b)
            result.append(item)
        return result or copy.deepcopy(defaults)

    def _shop_items(self, rows, defaults):
        result = []
        seen = set()
        for row in rows if isinstance(rows, list) else defaults:
            if not isinstance(row, dict):
                continue
            name = self._text(row.get("name"), "道具", 40)
            item_id = self._id(row.get("id"), name, seen)
            effect = self._text(row.get("effect"), "instant", 24)
            item = {
                "id": item_id,
                "name": name,
                "category": self._text(row.get("category"), "道具", 20),
                "price": self._int(row.get("price"), 1, 0, 1_000_000_000),
                "description": self._text(row.get("description"), "", 120),
                "effect": effect,
                "satiety_add": self._int(row.get("satiety_add"), 0, -100, 100),
                "mood_add": self._int(row.get("mood_add"), 0, -100, 100),
                "health_add": self._int(row.get("health_add"), 0, -100, 100),
                "energy_add": self._int(row.get("energy_add"), 0, -100, 100),
                "mood_min": self._int(row.get("mood_min"), 0, 0, 100),
                "mood_max": self._int(row.get("mood_max"), 0, 0, 100),
                "growth_min": self._int(row.get("growth_min"), 0, 0, 100_000),
                "growth_max": self._int(row.get("growth_max"), 0, 0, 100_000),
                "intimacy_min": self._int(row.get("intimacy_min"), 0, 0, 100_000),
                "intimacy_max": self._int(row.get("intimacy_max"), 0, 0, 100_000),
                "multiplier": self._float(row.get("multiplier"), 1, 0, 10),
                "daily_limit": self._int(row.get("daily_limit"), 0, 0, 1000),
                "weekly_limit": self._int(row.get("weekly_limit"), 0, 0, 1000),
                "enabled": bool(row.get("enabled", True)),
            }
            self._ensure_order(item, "mood_min", "mood_max")
            self._ensure_order(item, "growth_min", "growth_max")
            self._ensure_order(item, "intimacy_min", "intimacy_max")
            result.append(item)
        existing_ids = {str(item.get("id", "")) for item in result}
        existing_names = {str(item.get("name", "")) for item in result}
        for default_row in defaults:
            if not isinstance(default_row, dict):
                continue
            if str(default_row.get("id", "")) in existing_ids or str(default_row.get("name", "")) in existing_names:
                continue
            result.append(copy.deepcopy(default_row))
        return result or copy.deepcopy(defaults)

    def _care_services(self, rows, defaults):
        result = []
        seen = set()
        for row in rows if isinstance(rows, list) else defaults:
            if not isinstance(row, dict):
                continue
            name = self._text(row.get("name"), "护理", 40)
            service_id = self._id(row.get("id"), name, seen)
            result.append({
                "id": service_id,
                "name": name,
                "category": self._text(row.get("category"), "护理", 20),
                "base_price": self._int(row.get("base_price"), 0, 0, 1_000_000_000),
                "price_per_missing": self._int(row.get("price_per_missing"), 0, 0, 1_000_000),
                "target_health": self._int(row.get("target_health"), 0, 0, 100),
                "satiety_add": self._int(row.get("satiety_add"), 0, -100, 100),
                "mood_add": self._int(row.get("mood_add"), 0, -100, 100),
                "health_add": self._int(row.get("health_add"), 0, -100, 100),
                "energy_add": self._int(row.get("energy_add"), 0, -100, 100),
                "cooldown_seconds": self._int(row.get("cooldown_seconds"), 0, 0, 30_000_000),
                "enabled": bool(row.get("enabled", True)),
            })
        return result or copy.deepcopy(defaults)

    def _interactions(self, rows, defaults):
        result = []
        seen = set()
        for row in rows if isinstance(rows, list) else defaults:
            if not isinstance(row, dict):
                continue
            command = self._text(row.get("command"), "互动", 20)
            if command in seen:
                continue
            seen.add(command)
            item = {
                "command": command,
                "text": self._text(row.get("text"), "你陪她玩了一会儿。", 120),
                "mood_min": self._int(row.get("mood_min"), 1, 0, 100),
                "mood_max": self._int(row.get("mood_max"), 1, 0, 100),
                "intimacy_min": self._int(row.get("intimacy_min"), 1, 0, 100_000),
                "intimacy_max": self._int(row.get("intimacy_max"), 1, 0, 100_000),
                "growth_min": self._int(row.get("growth_min"), 1, 0, 100_000),
                "growth_max": self._int(row.get("growth_max"), 1, 0, 100_000),
                "energy_cost": self._int(row.get("energy_cost"), 0, 0, 100),
                "min_stage": self._int(row.get("min_stage"), 0, 0, 6),
                "enabled": bool(row.get("enabled", True)),
            }
            for a, b in [("mood_min", "mood_max"), ("intimacy_min", "intimacy_max"), ("growth_min", "growth_max")]:
                self._ensure_order(item, a, b)
            result.append(item)
        return result or copy.deepcopy(defaults)

    def _personalities(self, rows, defaults):
        defaults_by_name = {row.get("name"): row for row in defaults if isinstance(row, dict)}
        rows_by_name = {}
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, dict) and row.get("name"):
                    rows_by_name[str(row.get("name")).strip()] = row

        result = []
        for name, default_row in defaults_by_name.items():
            row = rows_by_name.get(name, {})
            item = {"name": name}
            for key, default_value in default_row.items():
                if key == "name":
                    continue
                if key == "enabled":
                    item[key] = bool(row.get(key, default_value))
                else:
                    item[key] = self._float(row.get(key), default_value, 0, 10)
            result.append(item)
        return result or copy.deepcopy(defaults)

    def _text_list(self, value, default, max_len, max_count):
        rows = value if isinstance(value, list) else default
        result = [self._text(x, "", max_len) for x in rows]
        result = [x for x in result if x][:max_count]
        return result or copy.deepcopy(default)

    def _text(self, value, default, max_len):
        text = str(value if value is not None else default).strip()
        text = re.sub(r"[\r\n\t]+", " ", text)
        return (text or default)[:max_len]

    def _id(self, value, name, seen):
        raw = str(value or "").strip().lower()
        raw = re.sub(r"[^a-z0-9_-]+", "_", raw)[:40].strip("_")
        if not raw:
            raw = f"job_{int(time.time() * 1000)}"
        base = raw
        idx = 2
        while raw in seen:
            raw = f"{base}_{idx}"
            idx += 1
        seen.add(raw)
        return raw

    def _int(self, value, default, low, high):
        try:
            value = int(float(value))
        except Exception:
            value = int(default)
        return max(int(low), min(int(high), value))

    def _float(self, value, default, low, high):
        try:
            value = float(value)
        except Exception:
            value = float(default)
        return max(float(low), min(float(high), value))

    def _ensure_order(self, obj, low_key, high_key):
        if obj[high_key] < obj[low_key]:
            obj[high_key] = obj[low_key]
