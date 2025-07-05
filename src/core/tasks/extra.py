import json
import random
import time
from typing import Dict, List, Tuple

from src.core.signer import Signer


class ExtraTask:
    def __init__(self, session, logger, config):
        self.session = session
        self.logger = logger
        self.config = config
        self.api = {
            "extra_list": "https://interface.music.163.com/api/music/partner/extra/wait/evaluate/work/list",
            "report_listen": "https://interface.music.163.com/weapi/partner/resource/interact/report"
        }
        self.signer = Signer(session, "", logger, config)  # task_id 为空字符串，因为上报听歌不需要

    def process_extra_tasks(self, task_id: str) -> None:
        """处理额外的评分任务"""
        try:
            extra_tasks, completed_count = self._get_extra_tasks()

            total_tasks = (7 if not self.config.get('full_extra_tasks', False) else len(extra_tasks) + completed_count)
            
            # 如果已经完成任务，直接返回
            if completed_count >= total_tasks:
                self.logger.info(f"今日已完成 {completed_count} 个额外评分任务，已达到每日上限")
                return
                
            if not extra_tasks:
                self.logger.info(f"额外评定完成数: {completed_count}")
                return

            self.logger.info(f"发现 {len(extra_tasks)} 个待额外评定任务")
            
            # 记录本次成功评分的数量
            success_count = 0
            remaining_tasks = total_tasks - completed_count
            
            for task in extra_tasks:
                if success_count >= remaining_tasks:
                    self.logger.info(f"已完成 {success_count} 个额外评分任务，总计完成 {completed_count + success_count} 个")
                    break
                    
                try:
                    work_name = task['work']['name']
                    self._process_single_task(task, task_id)
                    # 只有在没有抛出异常时才增加成功计数
                    success_count += 1
                    self.logger.info(f"成功完成第 {success_count}/{remaining_tasks} 个额外评分任务")
                    
                    # 添加随机等待时间
                    if success_count < remaining_tasks:  # 最后一个任务不需要等待
                        delay = self.config.get_wait_time()
                        self.logger.info(f"等待 {delay:.1f} 秒后继续...")
                        time.sleep(delay)
                        
                except Exception as e:
                    self.logger.warning(f"处理歌曲 {task['work']['name']} 失败，尝试下一个: {str(e)}")
                    continue

            self.logger.info(f"额外评分任务处理完成，成功评分 {success_count} 首")
            
            if success_count < remaining_tasks:
                self.logger.warning(f"未能完成所有额外评分任务，仅完成 {success_count}/{remaining_tasks} 个")

        except Exception as e:
            self.logger.error(f"处理额外评分任务时出错: {str(e)}")
            raise

    def _get_extra_tasks(self) -> Tuple[List[Dict], int]:
        """获取额外评分任务列表"""
        try:
            response = self.session.get(
                url=self.api["extra_list"],
                headers={"Referer": "https://mp.music.163.com/"}
            ).json()

            if response["code"] != 200:
                raise RuntimeError(f"获取额外任务失败: {response.get('message', '未知错误')}")

            extra_tasks = response["data"]
            completed_tasks = [t for t in extra_tasks if t['completed']]
            uncompleted_tasks = [t for t in extra_tasks if not t['completed']]
            
            # 获取所有未完成的任务，而不是只取前7个
            return uncompleted_tasks, len(completed_tasks)

        except Exception as e:
            self.logger.error(f"获取额外任务列表失败: {str(e)}")
            raise

    def _process_single_task(self, task: Dict, task_id: str) -> None:
        """处理单个额外评分任务"""
        work = task['work']
        try:
            # 1. 上报听歌记录
            self._report_listen(work)
            
            # 2. 评分
            signer = Signer(self.session, task_id, self.logger, self.config)
            signer.sign(work, is_extra=True)

        except Exception as e:
            self.logger.error(f"处理额外任务失败 - {work['name']}: {str(e)}")
            raise

    def _report_listen(self, work: Dict) -> None:
        """上报听歌记录"""
        try:
            csrf = self.session.cookies["__csrf"]
            
            # 准备加密数据
            data = {
                "workId": work['id'],
                "resourceId": work['resourceId'],
                "bizResourceId": "",
                "interactType": "PLAY_END",
                "csrf_token": csrf
            }
            
            # 使用相同的加密方式
            params = {
                "params": self.signer._get_params(data),
                "encSecKey": self.signer._get_enc_sec_key()
            }
            
            response = self.session.post(
                url=f"{self.api['report_listen']}?csrf_token={csrf}",
                data=params,
                headers={"Referer": "https://mp.music.163.com/"}
            ).json()

            if response["code"] != 200:
                raise RuntimeError(f"上报听歌记录失败: {response.get('message', '未知错误')}")
            else:
                self.logger.info(f"歌曲 {work['name']} 听歌记录上报成功")

        except Exception as e:
            self.logger.error(f"上报听歌记录失败: {str(e)}")
            raise