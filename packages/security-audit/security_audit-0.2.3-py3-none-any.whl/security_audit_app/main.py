from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Button, Static, Input, ProgressBar
from textual.containers import Vertical, Horizontal,ScrollableContainer,Grid
from textual import work
from textual_fspicker import FileOpen
import paramiko
import os
from typing import Optional
from importlib.resources import files
local_script_path=["generate_audit_report.sh","security_audit.sh"]
local_config_path=["data_for_report.csv","error_code_table.json"]
local_namu_path=["NanumGothic-Bold.ttf","NanumGothic-ExtraBold.ttf","NanumGothic-Regular.ttf"]

intro_text="""
리눅스 서버를 자동으로 점검하고 결과 보고서를 생성합니다. 
보고서는 PDF 또는 MD파일로 확인 가능합니다. 
원하는 서버 접속 방법을 선택해주세요

문의 메일: bc2430@naver.com 

"""

password_text="""
[패스워드로 서버에 접속할 경우]
점검할 서버의 ip와 계정명, 패스워드를 입력하여 접속을 시도합니다.

"""

ssh_text="""
[ssh키로 서버에 접속할 경우]
점검할 서버의 ip와 계정명, ssh 비밀키를 입력하여 접속을 시도합니다.
"""
class IntroScreen(Screen):
    """첫 프로그램 소개 화면"""
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="intro-container"):
            
            self.widget1 = Static("리눅스 서버 보안 점검 프로그램",expand=True)
            self.widget1.styles.color = "white"
            self.widget1.styles.border = ("heavy","white")
            self.widget1.styles.text_align=("center")
            self.widget1.styles.height = 3 
            yield self.widget1
                
            self.widget2 = Static(intro_text)
            self.widget2.styles.color = "white"
            self.widget2.styles.text_align=("center")
            yield self.widget2

            with Horizontal(id="intro-action-sections"):
                with Vertical(id="left-intro-section", classes="intro-section"):

                    self.widget3=Static(password_text)
                    yield self.widget3
                    self.widget3.styles.text_align=("center")
                    self.widget4=Button("시작하기",id="password_btn",variant="primary")

                    self.widget4.styles.content_align = ("right", "top")
                    yield self.widget4
    
                with Vertical(id="right-intro-section", classes="intro-section"):
                    self.widget5=Static(ssh_text)
                    yield self.widget5
                    self.widget5.styles.text_align=("center")              
                    self.widget6=Button("시작하기",id="ssh_btn",variant="primary")
                    yield self.widget6

        yield Footer()
    
    
    def on_button_pressed(self,event:Button.Pressed) -> None:
        if event.button.id == "password_btn": 
            self.app.push_screen("password_main")
        if event.button.id == "ssh_btn": 
            self.app.push_screen("ssh_main")
        
      
      
class PasswordMainScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Grid(id="connect_form_grid"):  

            self.widget7 = Static("서버 접속 정보 입력",expand=True)
            self.widget7.styles.color = "white"
            self.widget7.styles.border = ("heavy","white")
            self.widget7.styles.text_align=("center")
            self.widget7.styles.height = 3 
            yield self.widget7
            
            self.widget8 = Static("접속하려는 서버의 IP주소와 계정 정보를 입력해주세요",expand=True)
            self.widget8.styles.text_align=("center")
            yield self.widget8
            
            self.ip_input = Input(placeholder="input ip-address ex)192.168.0.1", type="text",id="ip_addr")
            yield self.ip_input
            self.account_input = Input(placeholder="input account name ", type="text",id="username")
            yield self.account_input
            self.password_input = Input(placeholder="input password ", type="text",id="password")
            yield self.password_input
            
            self.widget9=Button("접속", id="connect_password_btn",variant="primary")
            yield self.widget9
            self.widget10=Button("뒤로가기", id="back_btn",variant="primary")
            yield self.widget10

        yield Footer()  

    def on_button_pressed(self,event: Button.Pressed) -> None:
        if event.button.id == "connect_password_btn":
            ip_addr=self.query_one("#ip_addr",Input).value
            username=self.query_one("#username",Input).value
            password=self.query_one("#password",Input).value
            # ssh.close()  
            # self.app.notify("서버접속")
            self.app.push_screen(ProcessMainScreen(ip_addr=ip_addr,username=username,password=password))
        
        if event.button.id == "back_btn":
            self.app.push_screen("intro")
   

class SshMainScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Grid(id="connect_form_grid2"):

            self.widget11 = Static("서버 접속 정보 입력",expand=True)
            self.widget11.styles.color = "white"
            self.widget11.styles.border = ("heavy","white")
            self.widget11.styles.text_align=("center")
            self.widget11.styles.height = 3 
            yield self.widget11
            
            self.widget12 = Static("접속하려는 서버의 IP주소와 계정 정보를 입력해주세요",expand=True)
            self.widget12.styles.text_align=("center")
            yield self.widget12
            
            self.ip_input = Input(placeholder="input ip-address ex)192.168.0.1", type="text",id="ip_addr")
            yield self.ip_input
            self.account_input = Input(placeholder="input account name ", type="text",id="username")
            yield self.account_input
            yield Static("선택된 키 파일: ",id="display_ssh_key")
            self.ssh_input = Button("선택",id="search_ssh_file",variant="primary")
            yield self.ssh_input
            
            

            
            self.widget13=Button("접속", id="connect_ssh_btn",variant="primary")
            yield self.widget13
            self.widget14=Button("뒤로가기", id="back_btn",variant="primary")
            yield self.widget14

        yield Footer()      
    def on_button_pressed(self,event: Button.Pressed) -> None:
        if event.button.id == "connect_ssh_btn":
            ip_addr=self.query_one("#ip_addr",Input).value
            username=self.query_one("#username",Input).value
            

            # ssh.close()  
            # self.app.notify("서버접속")

            self.app.push_screen(ProcessMainScreen(ip_addr=ip_addr,username=username,keyfile_path=self.keyfile_path))
        
        if event.button.id == "back_btn":
            self.app.push_screen("intro")
        if event.button.id == "search_ssh_file":
            self.app.push_screen(FileOpen(title="SSH 키 파일 선택"), self.handle_keyfile_path)
            
    def handle_keyfile_path(self, keyfile_path: str) -> None:
        
        if keyfile_path:

            keyfile_path_str = str(keyfile_path)
            self.keyfile_path=keyfile_path_str
            display_widget=self.query_one("#display_ssh_key",Static)
            display_widget.update(f"선택된 키 파일: {keyfile_path_str}")
            self.app.notify("파일 선택이 완료되었습니다.")  

 
        else:
            self.app.notify("키 파일 선택이 취소되었습니다.")  
            
            
                  
class ProcessMainScreen(Screen):
    def __init__(self, ip_addr: str, username: str, 
             password: Optional[str] = None, 
             keyfile_path: Optional[str] = None, 
             **kwargs):
    
        super().__init__(**kwargs)
        # 전달받은 데이터를 클래스 내부 변수에 저장
        self.ip_addr = ip_addr
        self.username = username
        self.password = password
        self.keyfile_path=keyfile_path
        
        if not self.password and not self.keyfile_path:
            raise ValueError("비밀번호 또는 SSH 키 파일 경로 중 하나는 반드시 제공되어야 합니다.")
     
    def compose(self) -> ComposeResult:
        yield Header()
        self.widget16 = Static("서버 보안 점검및 파일 생성중",expand=True)
        self.widget16.styles.color = "white"
        self.widget16.styles.border = ("heavy","white")
        self.widget16.styles.text_align=("center")
        self.widget16.styles.height = 3 
        yield self.widget16
        yield ProgressBar(total=100, show_percentage=True, id="progressbar")
        
        with ScrollableContainer(id="log-scrool"):
            self.log_text="----------점검 로그 시작---------"
            yield Static(self.log_text,id="log_output")
        self.widget15=Button("처음으로", id="back_btn",variant="primary",)
        self.widget15.styles.display="none"
        yield self.widget15
        yield Footer()
    def on_button_pressed(self,event: Button.Pressed) -> None:
        if event.button.id == "back_btn":
            self.app.push_screen("intro")
            
    def on_mount(self):
        self.run_audit_process()
        
    def update_log(self,message:str):
        
        def update():
            self.log_text+=f"\n{message}"
            log_widget=self.query_one("#log_output")
            log_widget.update(self.log_text)
        self.call_later(update)
            
    @work(thread=True, exclusive=True)    
    def run_audit_process(self):
        if self.username == "root":
            remote_base_path=f"/{self.username}/audit_files"
        else:
            remote_base_path=f"/home/{self.username}/audit_files"
            
        
        remote_path1=f"{remote_base_path}/scripts"
        remote_path2=f"{remote_base_path}/config"
        remote_path3="/usr/share/fonts/truetype/nanum"
        remote_path4=f"{remote_base_path}/temp" # 만약 root가 아니면 remote_path3에 바로 파일전송 못하니 여기에 임시로 보내고 sudo권한으로 옮기기 위한 용도
        
        

        progressbar= self.query_one("#progressbar", ProgressBar)
        sftp = None  
        ssh = None 
        try:
            self.update_log("ssh 접속을 시도합니다.")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self.password:
                ssh.connect(hostname=self.ip_addr,username=self.username,password=self.password)
                self.update_log("ssh 접속에 성공했습니다.")
            elif self.keyfile_path:
                ssh.connect(hostname=self.ip_addr,username=self.username,key_filename=self.keyfile_path)
                self.update_log("ssh 접속에 성공했습니다.")
            else:
                self.app.notify("ssh접속에 실패했습니다.")

            self.call_later(progressbar.update, total=100, progress=10)

            self.update_log(f"서버로 점검을 위한 프로그램 송신중...")
            ssh.exec_command(f"mkdir -p {remote_path1}")
            ssh.exec_command(f"mkdir -p {remote_path2}")
            ssh.exec_command(f"mkdir -p {remote_path3}")
            ssh.exec_command(f"mkdir -p {remote_path4}")
            
  
            sftp=ssh.open_sftp()
            package_root = files("security-audit")
            for i, filename in enumerate(local_script_path):
                local_path = package_root.joinpath("scripts", filename)
                local_path = str(local_path)
                remote_file = f"{remote_path1}/{filename}"
                sftp.put(local_path, remote_file)
                self.update_log(f"전송완료 - {local_path}")
                # self.call_later(progressbar.advance(10+i*5))
                self.call_later(progressbar.update, total=100, progress=10+i*10)
                
            for i, filename in enumerate(local_config_path):
                local_path = package_root.joinpath("config", filename)
                local_path = str(local_path)
                remote_file = f"{remote_path2}/{filename}"
                sftp.put(local_path, remote_file)
                self.update_log(f"전송완료 - {local_path}")
                self.call_later(progressbar.update, total=100, progress=30+i*10)
            for i, filename in enumerate(local_namu_path):
                local_path = package_root.joinpath("Nanum_Gothic", filename)
                local_path = str(local_path)

                if self.username == "root":
                    remote_file = f"{remote_path3}/{filename}"
                else:
                    remote_file = f"{remote_path4}/{filename}"

                sftp.put(local_path, remote_file)
                self.update_log(f"전송완료 - {local_path}")
                self.call_later(progressbar.update, total=100, progress=60)
            
            self.update_log("프로그램 실행 권한 수정중...")
            ssh.exec_command(f"chmod u+x {remote_path1}/generate_audit_report.sh")
            ssh.exec_command(f"chmod u+x {remote_path1}/security_audit.sh")
            self.call_later(progressbar.update, total=100, progress=70)
            
            self.update_log("파일을 리눅스 서식으로 변환중...")
            ssh.exec_command(f"dos2unix {remote_path1}/security_audit.sh")
            ssh.exec_command(f"dos2unix {remote_path1}/generate_audit_report.sh")
            self.call_later(progressbar.update, total=100, progress=80)
    
            self.update_log("서버 점검 및 보고서 작성중...")
            stdin, stdout, stderr = ssh.exec_command(f"{remote_path1}/generate_audit_report.sh")
            output = stdout.read().decode().splitlines()
            report_md=output[-2].strip()
            report_pdf=output[-1].strip()
            
            self.update_log("서버 점검 및 보고서 작성 완료")
            self.call_later(progressbar.update, total=100, progress=90)    

            self.update_log("md파일 및 pdf 파일을 로컬로 다운 중...")
            local_home = os.path.expanduser("~")  
            local_path_md = os.path.join(local_home, report_md)
            local_path_pdf = os.path.join(local_home, report_pdf)
            self.call_later(progressbar.update, total=100, progress=95)

            
            if self.username == "root":
                sftp.get(f"/root/{report_md}",local_path_md)
                sftp.get(f"/root/{report_pdf}",local_path_pdf)
                
            else:
                sftp.get(f"/home/{self.username}/{report_md}",local_path_md)
                sftp.get(f"/home/{self.username}/{report_pdf}",local_path_pdf)
                
            self.update_log("md파일 및 pdf 파일 다운로드 완료!")
            self.call_later(progressbar.update, total=100, progress=100)
            self.widget15.styles.display="block"

        except Exception as e:
            self.app.notify(f"알 수 없는 오류 발생: {e}", severity="error") 
        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()
        
        
        
          
class Security_audit_program(App):
    CSS_PATH = "styles.tcss"
    SCREENS = { 
        "intro":IntroScreen,
        "password_main":PasswordMainScreen,
        "ssh_main":SshMainScreen
               }
    
    def on_mount(self) -> None:
        self.push_screen("intro")

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit the app") 
    ]



    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )




def main():
    app = Security_audit_program()
    app.run()


if __name__ == "__main__":
    main()
