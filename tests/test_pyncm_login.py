import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.config import Config
from src.utils.logger import Logger
from src.utils.auth import AuthService

def test_pyncm_login():
    """测试 pyncm 登录功能"""
    print("=== 测试 pyncm 登录功能 ===")
    
    try:
        # 初始化组件
        config = Config()
        logger = Logger()
        auth_service = AuthService(logger)
        
        # 获取登录凭据
        phone = config.get("netease_phone") or os.environ.get("NETEASE_PHONE")
        password = config.get("netease_password") or os.environ.get("NETEASE_PASSWORD")
        md5_password = config.get("netease_md5_password") or os.environ.get("NETEASE_MD5_PASSWORD")
        
        if not phone:
            print("❌ 未设置手机号，请在配置文件中设置 netease_phone 或设置环境变量 NETEASE_PHONE")
            return False
            
        if not md5_password and not password:
            print("❌ 未设置密码，请在配置文件中设置 netease_password 或 netease_md5_password")
            print("   或设置环境变量 NETEASE_PASSWORD 或 NETEASE_MD5_PASSWORD")
            return False
        
        print(f"📱 手机号: {phone[:3]}****{phone[-4:]}")
        print(f"🔑 密码类型: {'MD5' if md5_password else '明文'}")
        print("\n正在尝试登录...")
        
        # 执行登录
        success, cookies = auth_service.login(
            phone=phone,
            password=password if not md5_password else None,
            md5_password=md5_password
        )
        
        if success and cookies:
            print("✅ 登录成功！")
            print(f"🍪 MUSIC_U: {cookies['Cookie_MUSIC_U'][:20]}...")
            print(f"🍪 __csrf: {cookies['Cookie___csrf']}")
            
            # 验证 Cookie 格式
            music_u = cookies['Cookie_MUSIC_U']
            csrf = cookies['Cookie___csrf']
            
            if len(music_u) > 50:
                print("✅ MUSIC_U 格式正确")
            else:
                print("⚠️ MUSIC_U 格式可能不正确")
                
            if csrf:
                print("✅ __csrf 获取成功")
            else:
                print("⚠️ __csrf 为空")
                
            return True
        else:
            print("❌ 登录失败")
            return False
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装 pyncm 库: pip install pyncm")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

def main():
    """主函数"""
    print("pyncm 登录功能测试")
    print("=" * 50)
    
    if test_pyncm_login():
        print("\n🎉 所有测试通过！")
        print("您可以运行 python refresh_cookie.py 来刷新 Cookie")
    else:
        print("\n💥 测试失败")
        print("请检查配置和网络连接")

if __name__ == "__main__":
    main()
