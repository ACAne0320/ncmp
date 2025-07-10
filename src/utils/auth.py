import hashlib
from typing import Dict, Tuple, Optional
from ..utils.logger import Logger

try:
    from pyncm.apis.login import LoginViaCellphone
    from pyncm import GetCurrentSession, DumpSessionAsString
    PYNCM_AVAILABLE = True
except ImportError:
    PYNCM_AVAILABLE = False


class AuthService:
    def __init__(self, logger: Logger):
        self.logger = logger
        
        if not PYNCM_AVAILABLE:
            self.logger.error("pyncm 库未安装，无法使用登录功能")
            raise ImportError("pyncm 库未安装，请执行 pip install pyncm")
    
    def _hash_password(self, password: str) -> str:
        """将明文密码转换为 MD5 哈希"""
        return hashlib.md5(password.encode()).hexdigest()
        
    def login(self, phone: str, password: str = None, md5_password: str = None) -> Tuple[bool, Optional[Dict[str, str]]]:
        """
        通过手机号和密码登录获取 Cookie
        
        Args:
            phone: 手机号
            password: 明文密码（与md5_password二选一）
            md5_password: MD5加密后的密码（与password二选一）
            
        Returns:
            (成功状态, Cookie字典)
        """
        try:
            self.logger.info(f"尝试使用 pyncm 登录账号: {phone[:3]}****{phone[-4:]}")
            
            # 确定使用哪种密码
            if md5_password:
                password_hash = md5_password
                self.logger.debug("使用提供的MD5密码登录")
            elif password:
                password_hash = self._hash_password(password)
                self.logger.debug("使用明文密码（转换为MD5）登录")
            else:
                self.logger.error("未提供密码，无法登录")
                return False, None
            
            # 使用 pyncm 登录
            result = LoginViaCellphone(phone, passwordHash=password_hash, ctcode=86)
            
            # 检查登录结果
            if result.get("code") != 200:
                error_msg = result.get("message", "未知错误")
                self.logger.error(f"登录失败: {error_msg}")
                return False, None
            
            # 获取当前会话
            session = GetCurrentSession()
            
            # 从会话的 cookies 中获取
            music_u_cookie = session.cookies.get('MUSIC_U')
            csrf_cookie = session.cookies.get('__csrf')
            
            if not music_u_cookie:
                self.logger.error("未能从会话中获取 MUSIC_U cookie")
                return False, None
                
            if not csrf_cookie:
                self.logger.error("未能从会话中获取 __csrf cookie")
                return False, None
            
            # 构建返回的 Cookie 字典
            cookie_dict = {
                "Cookie_MUSIC_U": music_u_cookie,
                "Cookie___csrf": csrf_cookie
            }
            
            self.logger.info("登录成功并获取Cookie")
            self.logger.debug(f"成功获取MUSIC_U: {music_u_cookie[:10]}... 和 __csrf: {csrf_cookie}")
            
            # 记录会话信息（可选，用于调试）
            session_string = DumpSessionAsString(session)
            self.logger.debug(f"会话信息: {session_string[:50]}...")
            
            return True, cookie_dict
            
        except Exception as e:
            self.logger.error(f"pyncm 登录过程发生异常: {str(e)}")
            return False, None
