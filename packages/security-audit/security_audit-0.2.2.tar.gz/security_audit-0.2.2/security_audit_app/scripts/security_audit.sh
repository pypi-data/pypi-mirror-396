#!/bin/bash 

#========== 설정 ============

SCRIPT_DIR=$(cd "$(dirname $0)/../" && pwd )
TIMESTAMP=$(date "+%y%m%d_%H%M%S")
LOG_FILE=$SCRIPT_DIR/../audit_$TIMESTAMP.log

pass_cnt=0
fail_cnt=0
na_cnt=0

error_code=0 # 에러코드가 한가지 경우의 수만 존재할 경우 
error_code_array=(0 0 0 0 0 0 0 0 0 0 0 0) # 에러 코드가 복수가 가능할 경우 
declare -A warning_files 
audit_result=()
error_code_list=()      #일반경우일때의 에러코드를 보관하는 리스트
declare -A error_code_dict  #복잡할 경우. 키가 U_01이면 값이 (1 2 3) 이런식으로 경우에 대해 출력해야하는 모든 에러코드가 존재







passed_items=()
failed_items=()
na_items=()

#========== 함수 ============

log(){
    local level=$1
    local mesg=$2
    LOG_TIMESTAMP=$(date "+%y%m%d_%H%M%S")

    #echo "$mesg" 
    echo "[$LOG_TIMESTAMP][$level] $mesg" >> $LOG_FILE 
}



check_password_quality(){
    local key=$1 
    local min=$2
    local index=$3
    local value=$(grep -E "^[[:space:]]*$1[[:space:]]*=" "$file" | awk -F'=' '{gsub(/ /,"",$2); print $2}')

    if grep -qE "^[[:space:]]*$1[[:space:]]*=" "$file" ; then 
            if [ -n $value ] && [ $value -ge $min ]; then 
                log "INFO" "$key 설정 통과"
            else
                log "WARN" "$key 설정 부족"
                error_code_array[$index]=1
               ((error_code+=1)) 
        fi 
    else 
        log "WARN" "${key}이 설정되지 않았습니다"
            error_code_array[$index]=1
            ((error_code+=1)) 
    fi 

}


U_00(){

    
    echo "========== pts로그인 설정 확인 ============"

    if [ -f /etc/pam.d/login ]; then 
        if grep -Eq "^\s*auth\s+required\s+/lib/security/pam_securetty.so" /etc/pam.d/login; then 
            if [ -f /etc/securetty ]; then 
                if grep -Eq "^[[:space:]]*[^#]*pty" /etc/securetty; then 
                    log "WARN" "pty로 루트 로그인이 가능한 상태입니다."
                    error_code=1
                else 
                    log "INFO" "tty로만 root로그인이 가능합니다"
                    error_code=0
                fi
            else    
                log "NOTICE" "/etc/securetty파일이 존재하지 않습니다"
                error_code=10
            fi 
        else
            log "WARN" "auth required /lib/security/pam_securetty.so이 포함되어 있지 않습니다."
            error_code=2
        fi
    else 
        log "NOTICE" "/etc/pam.d/login 파일이 없습니다"
        error_code=11
    fi 

    if [ $error_code -eq 0 ]; then 
        log "INFO" "U_00테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")

    elif [ $error_code -gt 0 ] && [ $error_code -lt 10 ]; then 
        log "WARN" "U_00테스트 결과 취약"
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
    else 
        log "NOTICE" "U_00테스트 결과 경고"
        ((na_cnt+=1))
        na_items+=("${FUNCNAME[0]}")
    fi 

}



U_01(){
    
    echo "========== ssh 설정 확인 ============"
    if [ -f /etc/ssh/sshd_config ]; then 
        if sudo grep -qE "^[[:space:]]*passwordAuthentication[[:space:]]+yes" /etc/ssh/sshd_config; then 
            log "WARN" "passwordAuthentication yes 발견"
            error_code=1
        else
            log "INFO" "원격 비밀번호 로그인 불가능 설정 확인"
        fi 

        if sudo grep -qE "^[[:space:]]*PermitRootLogin[[:space:]]+yes" /etc/ssh/sshd_config; then 
            log "WARN" "PermitRootLogin yes 발견"
            error_code=2

        else
            log "INFO" "원격 루트 로그인 불가능 설정 확인"
        fi  
    else
        log "NOTICE" "ssh설정파일이 없습니다. ssh 설치 여부를 확인해주세요"
        error_code=10
    fi 


    if [ $error_code -eq 0 ]; then 
        log "INFO" "U_01테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")

    elif [ $error_code -gt 0 ] && [ $error_code -lt 10 ]; then 
        log "WARN" "U_01테스트 결과 취약"
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
    else 
        log "NOTICE" "U_01테스트 결과 경고"
        ((na_cnt+=1))
        na_items+=("${FUNCNAME[0]}")    
    fi 

}



U_02(){
    echo "========== 패스워드 복잡성 설정 ============"
    local lcredit=1 #소문자 최소 1자 이상 요구
    local ucredit=1 #최소 대문자 1자 이상 요구
    local dcredit=1 #최소 숫자 1자 이상 요구
    local ocredit=1 #최소 특수문자 1자 이상 요구
    local minlen=8  #최소 패스워드 길이 8자 이상 
    local file="/etc/security/pwquality.conf"

    if [ -f "$file" ]; then 
        check_password_quality "lcredit" "$lcredit" "1"
        check_password_quality "ucredit" "$ucredit" "2"
        check_password_quality "dcredit" "$dcredit" "3"
        check_password_quality "ocredit" "$ocredit" "4"
        check_password_quality "minlen" "$minlen" "5"
    else 
        log "WARN" "pwquality.conf 파일이 없습니다."
        error_code_array[10]=1
        error_code=10
    fi

    if [ $error_code -eq 0 ]; then 
        log "INFO" "U_02테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")

        error_code_array[0]=1
        
    elif [ "${error_code_array[10]}" -eq 1 ]; then 
        log "NOTICE" "U_02테스트 결과 경고"
        ((na_cnt+=1))
        na_items+=("${FUNCNAME[0]}") 
    else 
        log "WARN" "U_02테스트 결과 취약"
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
    fi        

}



U_03(){
    #계정 잠금 임계값이 10회 이하의 값으로 설정되어 있으면 통과
    file="/etc/pam.d/system-auth"

    echo "========== 계정 잠금 임계값 설정 ============"
    if [ -f $file ]; then 
        if sudo grep -qE "^\s*auth\s+required\s+/lib/security/pam_tally.so" "$file"; then 
            value=$(sudo grep "/lib/security/pam_tally.so" "$file" | grep -oP 'deny\s*=\s*\K[0-9]+')
            if [[ "$value" =~ ^[0-9]+$  ]] && [ $value -le 10 ]; then 
                log "INFO" "계정 잠금 임계값 결과 양호"
            else
                log "WARN" "deny설정이 없거나 10회 이상입니다"
                error_code=1
            fi 
        else 
            log "WARN" "pam_tally.so모듈을 사용하고 있지 않습니다"
            error_code=2

        fi
    else 
        log "NOTICE" "/etc/pam.d/system-auth 파일을 찾을 수 없습니다"
        error_code=10
    fi

    if [ $error_code -eq 0 ]; then 
        log "INFO" "U_03테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")

    elif [ $error_code -gt 0 ] && [ $error_code -lt 10 ]; then 
        log "WARN" "U_03테스트 결과 취약"
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
    else 
        log "NOTICE" "U_03테스트 결과 경고"
        ((na_cnt+=1))
        na_items+=("${FUNCNAME[0]}")    
    fi 

}

U_04(){
    echo "========== 패스워드 파일 보호 ============"
    if [ $(awk -F':' '$2 != "x"' /etc/passwd | wc -l) -gt 0 ]; then 
        log "WARN" "섀도 패스워드가 설정되어 있지 않습니다"
        log "WARN" "U_04테스트 결과 취약"
        error_code=1
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
        
    else
        log "INFO" "U_04테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")

    fi 
}

U_05(){
    #PATH 환경변수에 “.” 이 맨 앞이나 중간에 포함되지 않은 경우 + ::가 없는 경우 
    echo "========== 환경변수 경로 점검 ============"
    warning=$(echo $PATH | grep -E "\.:|::" | wc -l )
    if [ $warning -gt 0 ]; then 
        log "WARN" "환경변수 경로에 '.:' 혹은 '::'이 포함되어 있습니다"
        error_code=1
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
        log "WARN" "U_05테스트 결과 취약"

    else
        log "INRO" "환경변수 경로 검사 결과 양호"
        log "INFO" "U_05테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")

    fi 



}

U_06(){
    # 소유자가 존재하지 않는 파일/ 디렉터리가 존재하는지 
    echo "========== 파일 및 디렉토리 소유자 점검 ============"
    echo "점검중..."
    nouser_file_num=$(sudo find / -nouser -quit -print 2>/dev/null  | wc -l)
    nogroup_file_num=$(sudo find / -nogroup -quit -print 2>/dev/null | wc -l)

    if [ $nouser_file_num -gt 0 ] && [ $nogroup_file_num -gt 0 ]; then 
        log "WARN" "/etc/passwd에 등록되지 않은 유저와 그룹 소유의 파일 혹은 디렉토리가 존재합니다"
        log "WARN" "U_06테스트 결과 취약"
        error_code=1
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")

    elif [ $nouser_file_num -gt 0 ]; then 
        log "WARN" "/etc/passwd에 등록되지 않은 유저 소유의 파일 혹은 디렉토리가 존재합니다"
        log "WARN" "U_06테스트 결과 취약"
        error_code=2
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
    
    elif  [ $nogroup_file_num -gt 0 ]; then 
        log "WARN" "/etc/passwd에 등록되지 않은 그룹 소유의 파일 혹은 디렉토리가 존재합니다"
        log "WARN" "U_06테스트 결과 취약"
        error_code=3
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
    else
        log "INRO" "파일 및 디렉토리 소유자 점검 결과 양호"
        log "INFO" "U_06테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")

    fi 

}   

U_07(){
    echo "========== /etc/passwd파일 권한 점검 ============"

    if [ -f /etc/passwd ]; then 

        check=$(find /etc/passwd -type f -perm /0133 | wc -l)
        if [ $check -eq 1 ]; then 
            log "WARN" "/etc/passwd파일의 권한이 큽니다"
            log "WARN" "U_07테스트 결과 취약" 
            ((fail_cnt+=1))
            failed_items+=("${FUNCNAME[0]}")
            error_code=1
        else
            user=$(ls -l /etc/passwd | awk '{print $3}')
            group=$(ls -l /etc/passwd | awk '{print $4}')

            if [ $user = "root" ] && [ $group = "root" ]; then 
                log "INFO" "U_07테스트 결과 안전"
                ((pass_cnt+=1))
		        passed_items+=("${FUNCNAME[0]}")

            else
                log "WARN" "/etc/passwd파일의 소유자가 root가 아닙니다"
                log "WARN" "U_07테스트 결과 취약"  
                ((fail_cnt+=1))
                failed_items+=("${FUNCNAME[0]}")
                error_code=2                     
            fi

        fi

    else 
        log "NOTICE" "/etc/passwd파일이 존재하지 않습니다"
        log "NOTICE" "U_07테스트 결과 경고"
        ((na_cnt+=1))
        na_items+=("${FUNCNAME[0]}")    
        error_code=10                
    fi

}

U_08(){
    echo "========== /etc/shadow파일 권한 점검 ============"
    if [ -f /etc/shadow ]; then 

        check_000=$(find /etc/shadow -type f -perm 000 | wc -l )
        check_400=$(find /etc/shadow -type f -perm 400 | wc -l )

        if [ $check_000 -eq 0 ] && [ $check_400 -eq 0 ]; then 
            log "WARN" "/etc/passwd파일의 권한이 큽니다"
            log "WARN" "U_08테스트 결과 취약" 
            ((fail_cnt+=1))
            failed_items+=("${FUNCNAME[0]}")
            error_code=1


        else
            user=$(ls -l /etc/shadow | awk '{print $3}')
            group=$(ls -l /etc/shadow | awk '{print $4}')

            if [ $user = "root" ] && [ $group = "root" ]; then 
                log "INFO" "U_08테스트 결과 안전"
                ((pass_cnt+=1))
		        passed_items+=("${FUNCNAME[0]}")

            else
                log "WARN" "/etc/shadow파일의 소유자가 root가 아닙니다"
                log "WARN" "U_08테스트 결과 취약"   
                ((fail_cnt+=1))
                failed_items+=("${FUNCNAME[0]}")
                error_code=2                        
            fi 

            

        fi
    else 
        log "NOTICE" "/etc/shadow파일이 존재하지 않습니다"
        log "NOTICE" "U_08테스트 결과 취약"
        ((na_cnt+=1))
        na_items+=("${FUNCNAME[0]}")    
        error_code=10  
    fi

}

U_09(){
    echo "========== /etc/hosts파일 권한 점검 ============"
    if [ -f /etc/hosts ]; then 
        check=$(find /etc/hosts -type f -perm /0177 | wc -l)
        if [ $check -eq 1 ]; then 
            log "WARN" "/etc/hosts 파일의 권한이 큽니다"
            log "WARN" "U_09테스트 결과 취약" 
            ((fail_cnt+=1))
            failed_items+=("${FUNCNAME[0]}")
            error_code=1
        else
            user=$(ls -l /etc/hosts | awk '{print $3}')
            group=$(ls -l /etc/hosts | awk '{print $4}')

            if [ $user = "root" ] && [ $group = "root" ]; then 
                log "INFO" "U_09테스트 결과 안전"
                ((pass_cnt+=1))
		        passed_items+=("${FUNCNAME[0]}")

            else
                log "WARN" "/etc/hosts파일의 소유자가 root가 아닙니다"
                log "WARN" "U_09테스트 결과 취약"  
                ((fail_cnt+=1))
                failed_items+=("${FUNCNAME[0]}")
                error_code=2            
            fi

        fi

    else 
        log "NOTICE" "/etc/hosts파일이 존재하지 않습니다"
        log "NOTICE" "U_09테스트 결과 취약"
        ((na_cnt+=1))
        na_items+=("${FUNCNAME[0]}")    
        error_code=10 
    fi   
}


U_10(){
    # “/etc/xinetd.conf” 파일 및 “/etc/xinetd.d/” 하위 모든 파일의 소유자 및 권한 확인
    #ls –l /etc/xinetd.conf
    #ls –al /etc/xinetd.d/*
    #소유자가 root가 아니거나 파일의 권한이 600 이 아닌 경우
    
    echo "========== xinetd 관련 파일 권한 점검 ============"
    
    xinetd_conf=0 # 만약 검사 통과하면 1됨 
    xinetd_d=1    # 얘는 디렉토리이기 때문에 일단 1로 해놓고 만약 하나라도 이상하면 0으로 바꾸고 break하는 식

    if [ -f /etc/xinetd.conf ]; then 
        check=$(find /etc/xinetd.conf -type f -perm 600 | wc -l)
        if [ $check -eq 1 ]; then 
            user=$(ls -l /etc/xinetd.conf | awk '{print $3}')
            group=$(ls -l /etc/xinetd.conf | awk '{print $4}')
            if [ "$user" = "root" ] && [ "$group" = "root" ]; then 
                log "INFO" "/etc/xinetd.conf 검사 결과 양호"
                ((xinetd_conf+=1))
            else
                log "WARN" "/etc/xinetd.conf 파일의 소유자가 root가 아닙니다"
                error_code_array[1]=1
                error_code=1
            fi 
        else 
            log "WARN" "/etc/xinetd.conf 파일의 권한이 600이 아닙니다."
            error_code_array[2]=1
            error_code=2

        fi 

    else 
        log "NOTICE" "/etc/xinetd.conf파일이 존재하지 않습니다"
        error_code_array[10]=1
    fi 

    if [ -d /etc/xinetd.d ]; then 
        for file in /etc/xinetd.d/*; do 
            [ -f "$file" ] || continue
            check=$(find "$file" -type f -perm 600 | wc -l)
            if [ $check -ne 1 ]; then 
                log "WARN" "${file}의 파일 권한이 600이 아닙니다."
                error_code_array[3]=1
                ((xinetd_d-=1))
                break
            else
                user=$(ls -l "$file" | awk '{print $3}')
                group=$(ls -l "$file" | awk '{print $4}')
                if [ $user != "root" ] || [ $group != "root" ]; then 
                    log "WARN" "$file 파일의 소유자가 root가 아닙니다"
                    error_code_array[4]=1
                    ((xinetd_d-=1))
                    break

                fi 
            fi 
        done 
        

    else 
        log "NOTICE" "/etc/xinetd.d 디렉토리가 존재하지 않습니다"    
        error_code_array[11]=1

    fi 

    if [ $xinetd_conf -eq 1 ] && [ $xinetd_d -eq 0 ]; then 
        log "INFO" "U_10테스트 결과 안전"
        error_code_array[0]=1
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")

    elif [ "${error_code_array[10]}" -eq 1 ] || [ "${error_code_array[11]}" -eq 1 ]; then 
        log "NOTICE" "U_10테스트 결과 경고"
        ((na_cnt+=1))
        na_items+=("${FUNCNAME[0]}")
    else
        log "WARN" "U_10테스트 결과 취약"
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
    fi 
}

U_11(){
    echo "========== rsyslog.conf 파일 권한 점검 ============"
    #“rsyslog.conf” 파일의 소유자가 root가 아니거나 파일의 권한이 640이하인 경우 아래의 보안설정방법에 따라 설정을 변경함
    
    if [ -f /etc/rsyslog.conf ]; then 
        check=$(find /etc/rsyslog.conf -type f -perm /0137 | wc -l)
        if [ $check -eq 1 ]; then 
            log "WARN" "/etc/rsyslog.conf 파일의 권한이 큽니다"
            log "WARN" "U_11테스트 결과 취약"
            ((fail_cnt+=1))
            failed_items+=("${FUNCNAME[0]}")
            error_code=1

        else 
            user=$(ls -l /etc/rsyslog.conf | awk '{print $3}')
            group=$(ls -l /etc/rsyslog.conf | awk '{print $4}')
            if [ $user != "root" ] || [ $group != "root" ]; then 
                log "WARN" "/etc/rsyslog.conf 파일의 소유자가 root가 아닙니다"
                log "WARN" "U_11테스트 결과 취약"
                ((fail_cnt+=1))
                failed_items+=("${FUNCNAME[0]}")
                error_code=2
            else 
                log "INFO" "U_11테스트 결과 안전"
                ((pass_cnt+=1))
	        	passed_items+=("${FUNCNAME[0]}")

            fi 
        fi 

            

    else 
        log "NOTICE" "/etc/rsyslog.conf 파일이 존재하지 않습니다"
        ((na_cnt+=1))
        na_items+=("${FUNCNAME[0]}")
        error_code=10
    fi 
}

U_12(){
    echo "========== services 파일 권한 점검 ============"
    #/etc/services 파일의 소유자가 root가 아니거나 파일의 권한이 644 이하인 경우 아래의 보안설정방법에 따라 설정을 변경함
    
    if [ -f /etc/services ]; then 
        check=$(find /etc/services -type f -perm /0133 | wc -l)
        if [ $check -eq 1 ]; then 
            log "WARN" "/etc/services 파일의 권한이 큽니다"
            log "WARN" "U_12테스트 결과 취약"
            ((fail_cnt+=1))
            failed_items+=("${FUNCNAME[0]}")
            error_code=1
        else 
            user=$(ls -l /etc/services | awk '{print $3}')
            group=$(ls -l /etc/services | awk '{print $4}')
            if [ $user != "root" ] || [ $group != "root" ]; then 
                log "WARN" "/etc/services 파일의 소유자가 root가 아닙니다"
                log "WARN" "U_12테스트 결과 취약"
                ((fail_cnt+=1))
                failed_items+=("${FUNCNAME[0]}")
                error_code=2
            else 
                log "INFO" "U_12테스트 결과 안전"
                ((pass_cnt+=1))
		        passed_items+=("${FUNCNAME[0]}")

            fi 
        fi 

            

    else 
        log "NOTICE" "/etc/services 파일이 존재하지 않습니다"
        ((na_cnt+=1))
        na_items+=("${FUNCNAME[0]}")
        error_code=10
    fi 
}

#중요 파일들에 SUID 혹은 SGID중 하나라도 설정이 되있다면 취약. 
#파일이 없는건 취약 대상에서 뺌 
# 워닝파일 참고하면서 무슨 파일이 위험한지 표시하면 될듯
U_13(){
    echo "========== 불필요한 SUID,SGID 점검 ============"
    
    
    check_files=(
    "/sbin/dump"
    "/sbin/restore"
    "/sbin/unix_chkpwd"
    "/usr/bin/at"
    "/usr/bin/lpq"
    "/usr/bin/lpq-lpd"
    "/usr/bin/lpr"
    "/usr/bin/lpr-lpd"
    "/usr/bin/lprm"
    "/usr/bin/lprm-lpd"
    "/usr/bin/newgrp"
    "/usr/sbin/lpc"
    "/usr/sbin/lpc-lpd"
    "/usr/sbin/traceroute"
    )

    
    

    for file in "${check_files[@]}"; do 
        if [ ! -f $file ]; then 
            log "NOTICE" "$file 파일이 존재하지 않습니다."
        else 
            if ls -alL $file | awk '{print $1}' | grep -Eq '[sS]|[gG]'; then 
                warning_files["U_13"]+="$file " 
            fi 
        fi 

    done 


    if [ -n "${warning_files["U_13"]}" ]; then 
        for file in "${warning_files[@]}"; do 
            echo "SUID 혹은 SGID가 설정된 파일: $file"
        done 

        log "WARN" "U_13테스트 결과 취약"
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
        error_code=1
    else 
        log "INFO" "U_13테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")


    fi 

}

#사용자 홈 디렉토리 환경파일의 소유자가 root혹은 자신으로 지정되어있고, root와 소유자만 쓰기가 가능한 경우
#얘도 워닝파일 보면서 이런 파일들 문제 있으니까 고쳐라라고 하면 될듯 
U_14(){
    echo "========== 사용자 환경파일 소유자 및 권한 점검 ============"

    
    env_files=(
    ".profile"
    ".kshrc"
    ".cshrc"
    ".bashrc"
    ".bash_profile"
    ".login"
    ".exrc"
    ".netrc"
    )
    error=0
    users=($(ls /home))

    for user in "${users[@]}"; do 
        for file in "${env_files[@]}"; do 
            if [ ! -f /home/"$user"/"$file" ]; then 
                log "NOTICE" "/home/"$user"/"$file" 환경파일이 존재하지 않습니다"
                continue
            fi 

            file_owner=$(ls -al /home/"$user"/"$file" | awk '{print $3}') 
            if [ $file_owner != "root" ] && [ $file_owner != "$user" ]; then 
                log "WARN" "/home/"$user"/"$file" 파일 소유자를 확인해주세요"
                warning_files["U_14"]+="$file "
                ((error+=1))
            else
                check=$(find "/home/"$user"/"$file"" -type f -perm /0022 | wc -l)
                if [ $check -eq 1 ]; then 
                    log "WARN" "/home/"$user"/"$file" 파일의 그룹 혹은 아더가 쓰기 기능을 갖고 있습니다"
                    warning_files["U_14"]+="$file " 
                    ((error+=1))

                    continue
                fi 
            fi 
        done 
    done      

    if [ $error -eq 0 ]; then 
        log "INFO" "U_14테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")

        error_code=0
    else 
        log "WARN" "U_14테스트 결과 취약"
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
        error_code=1

    fi 

    
   

}

#아더에 쓰기권한이 있는 파일을 world writable 파일이라고 함 
#가상파일은 제외하고 이 파일이 있다면 일단 경고 보내기 
U_15(){
    echo "========== world writable 파일 점검 ============"
    ww_files=$(find / -path /proc -prune -o -path /sys -prune -o -path /dev -prune -o -type f -perm -2 2>/dev/null)
    if [ -z "$ww_files" ]; then 
        log "INFO" "U_15테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")

    else 
        echo "발견된 world writable 파일: $ww_files"
        log "WARN" "U_15테스트 결과 취약"
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
        error_code=1

    fi
}

U_16(){
    echo "========== /dev에 존재하지 않는 device 파일 점검 ============"
    if [ $(find /dev -type f -exec ls -l {} \; | wc -l ) -eq 0 ]; then 
        log "INFO" "U_16테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")

    else 
        log "WARN" "U_16테스트 결과 취약"
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
        error_code=1
    fi 

}

#/etc/hosts.deny 파일에 ALL:ALL 설정이 없거나 /etc/hosts.allow 파일에 ALL:ALL 설정이 있을 경우 취약으로 판단
U_17(){
    echo "========== 접속 IP 및 포트 제한 ============"

    if [ -f /etc/hosts.deny ]; then 
        if grep -Eiq '^\s*ALL\s*:\s*ALL\s*$' /etc/host.deny; then 
            if [ -f /etc/hosts.allow ]; then 
                if grep -Eiq '^\s*ALL\s*:\s*ALL\s*$' /etc/host.allow; then 
                    log "WARN" "/etc/hosts.allow 파일에 ALL:ALL 설정이 있습니다."
                    log "WARN" "U_17테스트 결과 취약"
                    ((fail_cnt+=1))
                    failed_items+=("${FUNCNAME[0]}")
                    error_code=1
                    break                    
                else 
                    log "INFO" "U_17테스트 결과 안전" 
                    ((pass_cnt+=1))
		            passed_items+=("${FUNCNAME[0]}")

                    break
                fi
            else 
                log "INFO" "/etc/hosts.allow 파일이 없습니다"
                log "INFO" "U_17테스트 결과 안전" # /etc/hosts.allow은 없어도 괜찮음.
                ((pass_cnt+=1))
		        passed_items+=("${FUNCNAME[0]}")

            fi
        else 
            log "WARN" "/etc/hosts.deny 파일에 ALL:ALL 설정이 없습니다."
            log "WARN" "U_17테스트 결과 취약"
            ((fail_cnt+=1))
            failed_items+=("${FUNCNAME[0]}")
            error_code=2
            break
        fi

    else 
        log "NOTICE" "/etc/hosts.deny 파일이 없습니다."
        log "NOTICE" "tcp_wrappers를 사용중이라면 U_17테스트 결과 취약 "
        ((na_cnt+=1))
        na_items+=("${FUNCNAME[0]}")
        error_code=10
    fi 
}

U_18(){
    echo "========== finger서비스 활성화 유무 점검 ============"

    if ls -alL /etc/xinetd.d/* 2>/dev/null | grep -Eiq "echo finger" ; then
        log "WARN" "finger서비스가 활성화 중입니다. "
        log "WARN" "U_18테스트 결과 취약"
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
        error_code=1
    else 
        log "INFO" "U_18테스트 결과 안전" # 단, xinetd를 사용할 경우
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")


    fi
}

U_19(){
    echo "========== FTP 계정 유무 점검 ============"
    if cat /etc/passwd | grep -q "ftp"; then 
        log "WARN" "FTP계정이 존재합니다"
        log "WARN" "U_19테스트 결과 취약"
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
        error_code=1
    else 
        log "INFO" "U_19테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")


    fi 

}

U_20(){
    echo "========== r 계열 서비스 비활성화 점검 ============"
    if ls -alL /etc/xinetd.d/*  2>/dev/null | egrep "rsh|rlogin|rexec" | egrep -vq "grep|klogin|kshell|kexec"; then 
        log "WARN" "r계열 서비스가 실행중입니다."
        log "WARN" "U_20테스트 결과 취약"
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
        error_code=1
    else
        log "INFO" "U_20테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")


    fi 

}

U_21(){
    #ls -al /usr/bin/crontab 이 실행파일을 640 이하이고 소유자가 root임을 확인해야 함. 
    #그리고 crontab cron.hourly cron.daily cron.weekly cron.monthly cron.allow cron.deny 이 파일 및 디렉토리에 대해서도 확인해야함
    echo "========== crond 파일 소유자 및 권한 설정 ============"
    error=0
    files=(
        /usr/bin/crontab
        /etc/crontab
        /etc/cron.hourly 
        /etc/cron.daily 
        /etc/cron.weekly 
        /etc/cron.monthly 
        /etc/cron.allow 
        /etc/cron.deny)
        
    for file in "${files[@]}"; do 
        if [ ! -f $file ] && [ ! -d $file ]; then 
            log "WARN" "$file 파일 혹은 디렉토리가 존재하지 않습니다."
            continue
        else 
            if [ -f $file ]; then 
                check=$(find $file -type f -perm /0137 | wc -l )
                if [ $check -gt 0 ]; then 
                    log "WARN" "$file 파일의 권한이 너무 큽니다."
                    warning_files["U_21"]+="$file "
                    ((error+=1))
                    else
                    file_owner=$(ls -l $file | awk '{print $3}')
                    if [ $file_owner = "root" ]; then 
                        log "INFO" "$file 파일 테스트 결과 양호"
                    else
                        log "WARN" "$file 파일 소유자가 root가 아닙니다."
                        warning_files["U_21"]+="$file "
                        ((error+=1))

                    fi 
                fi 
            elif [ -d $file ]; then 
                  shopt -s nullglob
                  for sub_file in $file/*; do 
                     check=$(find $sub_file -type f -perm /0137 | wc -l )
                        if [ $check -gt 0 ]; then 
                            log "WARN" "$sub_file 파일의 권한이 너무 큽니다."
                            warning_files["U_21"]+="$file "
                            ((error+=1))

                        else
                            file_owner=$(ls -l $sub_file | awk '{print $3}')
                            if [ $file_owner = "root" ]; then 
                                log "INFO" "$sub_file 파일 테스트 결과 양호"
                            else
                                log "WARN" "$sub_file 파일 소유자가 root가 아닙니다."
                                warning_files["U_21"]+="$file "
                                ((error+=1))

                            fi 
                        fi 
                    done 
                    shopt -u nullglob
            else
                continue
            fi 
        fi 
    done 

    if [ $error -eq 0 ]; then 
        log "INFO" "U_21테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")

    else
        log "WARN" "U_21테스트 결과 취약"
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
        error_code=1
    fi 

}

U_22(){

    # redhat 9버전 이후에는 xinetd -> systemctl로 바꼈다고 함 
    # systemctl로 하자 xinetd는 2013년에 지원 종료됐음. 
    echo "========== DoS 공격에 취약한 서비스 비활성화  ============"
    error=0
    services=(
        echo
        discard
        daytime
        charge
        ntp
        dns 
        snmp
    )
 
    for service in "${services[@]}"; do 
        if [ $(systemctl is-active $service) = "active" ]; then 
            log "WARN" "$service 서비스가 동작중입니다."
            warning_files["U_22"]+="$service "
            ((error+=1))
        fi 
    done 

    if [ $error -gt 0 ]; then
        log "WARN" "U_22테스트 결과 취약"
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
        error_code=1

    else
        log "INFO" "U_22테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")

    fi 


    
}

U_23(){
    echo "========== NFS 서비스 점검 ============"
    error=0
    services=(
        nfs
        statd
        lockd
    )
 
    for service in "${services[@]}"; do 
        if [ $(systemctl is-active $service) = "active" ]; then 
            log "WARN" "$service 서비스가 동작중입니다."
            warning_files["U_23"]+="$file "
            ((error+=1))
        fi 
    done 

    if [ $error -gt 0 ]; then
        log "WARN" "U_23테스트 결과 취약"
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
        error_code=1
    else
        log "INFO" "U_23테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")

    fi 
    
}

U_24(){
    # 접근 권한에 everyone(*)이 있으면 일단 경고 보내는 함수
    echo "========== NFS 접근 권한 확인 ============"

    if [ -f /etc/exports ]; then 
        if grep -Eq "^[^#]*\*" /etc/exports; then 
            log "WARN" "접근권한에 *가 포함되어 있습니다. "
            log "WARN" "U_24테스트 결과 취약"
            ((fail_cnt+=1))
            failed_items+=("${FUNCNAME[0]}")
            error_code=1
            
        else 
            log "INFO" "U_24테스트 결과 안전"
            ((pass_cnt+=1))
		    passed_items+=("${FUNCNAME[0]}")


        fi 
    else 
        log "NOTICE" "/etc/exports 파일이 존재하지 않습니다."
        log "NOTICE" "U_24테스트 결과 점검불가"
        ((na_cnt+=1))
        na_items+=("${FUNCNAME[0]}")
        error_code=10

    fi 

}


U_25(){
    echo "========== automountd 서비스 점검 ============"
    if [ $(systemctl is-active automountd) = "active" ]; then 
    
        log "WARN" "automount 서비스가 동작중입니다."
        error_code=1
    fi 


    if [ $error_code -gt 0 ]; then
        log "WARN" "U_25테스트 결과 취약"
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")

    else
        log "INFO" "U_25테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")


    fi 
    
}

U_26(){
    echo "========== RPC 서비스 점검 ============"

    services=(
    rpc.cmsd
    rpc.ttdbserverd
    sadmind
    rusersd
    walld
    sprayd
    rstatd
    rpc.nisd
    rexd
    rpc.pcnfsd
    rpc.statd
    rpc.ypupdated
    rpc.rquotad
    kcms_server
    cachefsd
    )

 
    for service in "${services[@]}"; do 
        if [ $(systemctl is-active $service) = "active" ]; then 

            log "WARN" "$service 서비스가 동작중입니다."
            ((error+=1))
            warning_files["U_26"]+="$service "

        fi 
    done 

    if [ $error -gt 0 ]; then
        log "WARN" "U_26테스트 결과 취약"
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
        error_code=1
    else
        log "INFO" "U_26테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")

    fi 
    
}

U_27(){
    echo "========== NIS, NIS+ 점검 ============"
    error=0
    services=(
        ypserv 
        ypbind 
        ypxfrd
        rpc.yppasswdd
        rpc.ypupdated
    )

    for service in "${services[@]}"; do 
        if [ $(systemctl is-active $service) = "active" ]; then 
            log "WARN" "$service 서비스가 실행중입니다."
            warning_files["U_27"]+="$service "
            ((error+=1))
        fi 
    done 

    if [ $error -gt 0 ]; then
        log "WARN" "U_27테스트 결과 취약"
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
        error_code=1
    else
        log "INFO" "U_27테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")


    fi 


}


U_28(){
    echo "========== tftp, talk 서비스 점검 ============"
    error=0
    services=(
        tftp
        talk
        ntalk
    )

    for service in "${services[@]}"; do 
        if [ $(systemctl is-active $service) = "active" ]; then 
            log "WARN" "$service 서비스가 실행중입니다."
            warning_files["U_28"]+="$service "
            ((error+=1))
        fi 
    done 

    if [ $error -gt 0 ]; then
        log "WARN" "U_28테스트 결과 취약"
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
        error_code=1
    else
        log "INFO" "U_28테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")


    fi 


}


U_29(){
    echo "========== 스팸 메일 릴레이 제한 ============"
    if [ $(systemctl is-active sendmail.service ) = "inactive" ]; then 
        log "INFO" "sendmail 서비스 사용중이 아닙니다."
        log "INFO" "U_29테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")

        

    else 
        if [ -f /etc/mail/sendmail.cf ]; then 
            if grep -Eq "^[[:space:]]*[^#].*R\$.*550 Relaying denied" /etc/mail/sendmail.cf; then
                log "INFO" "스팸 메일 릴레이 제한이 설정된 상태입니다."
                log "INFO" "U_29테스트 결과 안전"
                ((pass_cnt+=1))
		        passed_items+=("${FUNCNAME[0]}")



            else 
                log "WARN" "스팸 메일 릴레이 제한을 설정해주세요."
                log "WARN" "U_29테스트 결과 취약"
                ((fail_cnt+=1))
                failed_items+=("${FUNCNAME[0]}")
                error_code=1
            fi

        else 
            log "NOTICE" "/etc/mail/sendmail.cf 파일이 존재하지 않습니다."
            log "NOTICE" "U_29테스트 점검불가"        
            ((na_cnt+=1))
            na_items+=("${FUNCNAME[0]}")
            error_code=10

        fi 
    fi 

}

U_30(){
    echo "========== 일반사용자의 Sendmail 실행 방지 ============"

    if [ $(systemctl is-active sendmail.service ) = "inactive" ]; then 
            log "INFO" "sendmail 서비스 사용중이 아닙니다."
            log "INFO" "U_30테스트 결과 안전"
            ((pass_cnt+=1))
		    passed_items+=("${FUNCNAME[0]}")


    else 
        if [ -f /etc/mail/sendmail.cf ]; then 
            if grep -Eq "^[[:space:]]*[^#]*PrivacyOptions[^#]*restrictqrun" /etc/mail/sendmail.cf; then
                log "INFO" "일반 사용자의 Sendmail실행 방지가 설정되어 있습니다."
                log "INFO" "U_30테스트 결과 안전"
                ((pass_cnt+=1))
		        passed_items+=("${FUNCNAME[0]}")



            else 
                log "WARN" "일반 사용자의 Sendmail실행 방지가 설정되어 있지 않습니다."
                log "WARN" "U_30테스트 결과 취약"
                ((fail_cnt+=1))
                failed_items+=("${FUNCNAME[0]}")
                error_code=1
            fi

        else 
            log "NOTICE" "/etc/mail/sendmail.cf 파일이 존재하지 않습니다."
            log "NOTICE" "U_30테스트 점검불가"        
            ((na_cnt+=1))
            na_items+=("${FUNCNAME[0]}")
            error_code=10
        fi 

    fi 
    
}





#/etc/named.conf 파일에 allow-transfer { any; } 설정이 있으면 취약 
U_31(){
    echo "========== DNS Zone Transfer 점검 ============"
    if [ "$(systemctl is-active named )" = "inactive" ]; then 
            log "INFO" "DNS 서비스 사용중이 아닙니다."
            log "INFO" "U_31테스트 결과 안전"
            ((pass_cnt+=1))
		    passed_items+=("${FUNCNAME[0]}")


    else 
        if [ -f /etc/named.conf ]; then 
            if [ $(grep -vE "^[[:space:]]*#" /etc/named.conf | grep -i "allow-transfer"  | grep -i "any" | wc -l) -gt 0 ]; then 
                log "WARN" "Zone Transfer를 모든 사용자에게 허용중입니다."
                log "WARN" "U_31테스트 결과 취약 "
                ((fail_cnt+=1))
                failed_items+=("${FUNCNAME[0]}")
                error_code=1
            else 
                log "INFO" "Zone Transfer를 허가된 사용자에게만 허용중입니다."
                log "INFO" "U_31테스트 결과 안전"
                ((pass_cnt+=1))
		        passed_items+=("${FUNCNAME[0]}")


    
            fi 

        else 
            log "NOTICE" "/etc/named.conf 설정파일이 존재하지 않습니다."
            log "NOTICE" "U_31테스트 점검불가" 
            ((na_cnt+=1))
            na_items+=("${FUNCNAME[0]}")
            error_code=10
        fi 
    fi 

}

U_32(){
    #/etc/httpd/conf/httpd.conf에 Options Indexes 가 포함되어 있으면 index.html이 없을때 디렉토리 안 파일 내용을 다 보여주니 취약
    echo "========== 웹서비스 디렉토리 리스팅 점검 ============"
    if [ -f /etc/httpd/conf/httpd.conf ]; then   
        if [ "$(grep -i "^[[:space:]]*[^#]*Options[^#]*Indexes" /etc/httpd/conf/httpd.conf | wc -l)" -gt 0 ]; then 
            log "WARN" "웹서비스 디렉토리 리스팅이 작동중입니다."
            log "WARN" "U_32테스트 결과 취약 "
            ((fail_cnt+=1))
            failed_items+=("${FUNCNAME[0]}")
            error_code=1
        else
            log "INFO" "U_32테스트 결과 안전"
            ((pass_cnt+=1))
		    passed_items+=("${FUNCNAME[0]}")


        fi
    else 
        log "NOTICE" "/etc/httpd/conf/httpd.conf 설정파일이 존재하지 않습니다."
        log "NOTICE" "U_32테스트 점검불가"  
        ((na_cnt+=1))
        na_items+=("${FUNCNAME[0]}")
        error_code=10
    fi 
}

U_33(){
    # /etc/httpd/conf/httpd.conf에서 User root Group root 이런식이면 취약 
    echo "========== 웹서비스 웹 프로세스 권한 제한 ============"
    error=0
    if [ -f /etc/httpd/conf/httpd.conf ]; then   
        if [ "$(grep "^[[:space:]]*User[[:space:]]*root"  /etc/httpd/conf/httpd.conf | wc -l )" -gt 0 ]; then 
            log "WARN" "Apache 데몬이 root 유저 권한으로 작동중입니다."
            ((error+=1))
            error_code=1

        fi 
        if [ "$(grep "^[[:space:]]*Group[[:space:]]*root"  /etc/httpd/conf/httpd.conf | wc -l )" -gt 0 ]; then 
            log "WARN" "Apache 데몬이 root 그룹 권한으로 작동중입니다."
            ((error+=1))   
            error_code=2

        fi 

        if [ $error -gt 0 ]; then 
            log "WARN" "U_33테스트 결과 취약 " 
            ((fail_cnt+=1))
            failed_items+=("${FUNCNAME[0]}")

        else 
            log "INFO" "U_33테스트 결과 안전"
            ((pass_cnt+=1))
		    passed_items+=("${FUNCNAME[0]}")


        fi 
    else 
        log "NOTICE" "/etc/httpd/conf/httpd.conf 설정파일이 존재하지 않습니다."
        log "NOTICE" "U_33테스트 점검불가"  
        ((na_cnt+=1))
        na_items+=("${FUNCNAME[0]}")
        error_code=10

    fi 

}

U_34(){
    #/etc/httpd/conf/httpd.conf에 AllowOverride None가 하나라도 들어있으면 안됨 
    echo "========== 웹서비스 상위 경로 이동 가능 여부 점검 ============"
    if [ -f /etc/httpd/conf/httpd.conf ]; then   
        if [ "$(grep "^[[:space:]]*AllowOverride[[:space:]]*None"  /etc/httpd/conf/httpd.conf | wc -l )" -gt 0 ]; then 
            log "WARN" "U_34테스트 결과 취약 " 
            ((fail_cnt+=1))
            failed_items+=("${FUNCNAME[0]}")
            error_code=1
        else 
            log "INFO" "U_34테스트 결과 안전"
            ((pass_cnt+=1))
		    passed_items+=("${FUNCNAME[0]}")

        fi 
    else 
        log "NOTICE" "/etc/httpd/conf/httpd.conf 설정파일이 존재하지 않습니다."
        log "NOTICE" "U_34테스트 점검불가"  
        ((na_cnt+=1))
        na_items+=("${FUNCNAME[0]}")
        error_code=10   
    fi 

}


# /usr/share/httpd/htdocs/manual 랑 /usr/share/httpd/manual 두 디렉터리 중 하나라도 존재하면 취약으로 하면 될듯 
U_35(){
    echo "========== 웹서비스 불필요한 파일 존재 여부 점검 ============"
    error=0

    if [ -d /usr/share/httpd/htdocs/manual ]; then 
        log "WARN" "/usr/share/httpd/htdocs/manual 디렉터리가 존재합니다."
        error_code=1
        error_code_array[1]=1
        warning_files["U_35"]+="/usr/share/httpd/htdocs/manual "
        ((error+=1))
    fi 
    if [ -d /usr/share/httpd/manual ]; then 
        log "WARN" "/usr/share/httpd/manual 디렉터리가 존재합니다."
        warning_files["U_35"]+="/usr/share/httpd/manual "
        error_code=2
        error_code_array[2]=1
        ((error+=1))
    fi     
    if [ $error -gt 0 ]; then 
        log "WARN" "U_35테스트 결과 취약 " 
        ((fail_cnt+=1))
        failed_items+=("${FUNCNAME[0]}")
    else 
        log "INFO" "U_35테스트 결과 안전"
        ((pass_cnt+=1))
		passed_items+=("${FUNCNAME[0]}")

    fi
    
}


U_36(){
    echo "========== 웹서비스 링크 사용금지 점검 ============"
    if [ -f /etc/httpd/conf/httpd.conf ]; then  

        if [ "$(grep -i "^[[:space:]]*[^#]*Options[^#]*FollowSymLinks" /etc/httpd/conf/httpd.conf | wc -l)" -gt 0 ] &&
            [ "$(grep -i "^[[:space:]]*[^#]*Options[^#]*-FollowSymLinks" /etc/httpd/conf/httpd.conf | wc -l)" -eq 0 ] ; then 
            log "WARN" "심볼릭 링크, aliases가 사용 가능한 상태입니다."
            log "WARN" "U_36테스트 결과 취약 "
            ((fail_cnt+=1))
            failed_items+=("${FUNCNAME[0]}")
            error_code=1
        else
            log "INFO" "U_36테스트 결과 안전"
            ((pass_cnt+=1))
		    passed_items+=("${FUNCNAME[0]}")

        fi
    else 
        log "NOTICE" "/etc/httpd/conf/httpd.conf 설정파일이 존재하지 않습니다."
        log "NOTICE" "U_36테스트 점검불가"  
        ((na_cnt+=1))
        na_items+=("${FUNCNAME[0]}")
        error_code=10
    fi 
}




#LimitRequestBody가 설정되어 있는지, 있다면 모든 디렉토리에 대해 설정용량을 보고 제일 큰게 5메가 이상인지 확인 
U_37(){
    echo "========== 웹서비스 파일 업로드 및 다운로드 제한 ============"
    if [ -f /etc/httpd/conf/httpd.conf ]; then  
        if [ "$(grep -i "^[^#]*LimitRequestBody" /etc/httpd/conf/httpd.conf | wc -l )" -gt 0 ]; then 
            if [ "$(grep -i "^[^#]*LimitRequestBody" /etc/httpd/conf/httpd.conf | awk '{print $2}' | sort -nr | head -n 1)" -gt 5000000 ]; then 
                log "NOTICE" "업로드 및 다운로드 파일이 5M 초과로 설정되어 있는 디렉토리가 존재합니다."
                log "NOTICE" "U_37테스트 결과 주의"
                ((na_cnt+=1))
                na_items+=("${FUNCNAME[0]}")
                error_code=11
            else 
                log "INFO" "U_37테스트 결과 안전"
                ((pass_cnt+=1))
		        passed_items+=("${FUNCNAME[0]}")


            fi 
        else
            log "WARN" "LimitRequestBody가 설정되어 있지 않습니다."
            log "WARN" "U_37테스트 결과 취약 "
            ((fail_cnt+=1))
            failed_items+=("${FUNCNAME[0]}")
            error_code=1
        fi 

    else 
        log "NOTICE" "/etc/httpd/conf/httpd.conf 설정파일이 존재하지 않습니다."
        log "NOTICE" "U_37테스트 점검불가"  
        ((na_cnt+=1))
        na_items+=("${FUNCNAME[0]}")
        error_code=10
    fi 
    
}


U_38(){
    echo "========== 웹서비스 영역의 분리 ============"
    if [ -f /etc/httpd/conf/httpd.conf ]; then  
        if [ "$(grep -i "^[^#]*DocumentRoot" /etc/httpd/conf/httpd.conf | wc -l )" -gt 0 ]; then 
            document_root="$(grep -i "^[^#]*DocumentRoot" /etc/httpd/conf/httpd.conf | awk '{gsub(/"/,"",$2); print $2}' | head -n 1)"
            if [ "$document_root" = "/usr/local/apache/htdocs" ] || [ "$document_root" = "/usr/local/apache2/htdocs" ] || [ "$document_root" = "/var/www/html" ]; then 
                log "WARN" "DocumentRoot가 기본 디렉토리로 설정되어 있습니다."
                log "WARN" "U_38테스트 결과 취약 "
                ((fail_cnt+=1))
                failed_items+=("${FUNCNAME[0]}")
                error_code=1
                error_code_array[1]=1
            else 
                log "INFO" "U_38테스트 결과 안전"
                ((pass_cnt+=1))
		        passed_items+=("${FUNCNAME[0]}")

            fi 
        else
            log "WARN" "DocumentRoot가 설정되어 있지 않습니다."
            log "WARN" "U_38테스트 결과 취약"
            ((fail_cnt+=1))
            failed_items+=("${FUNCNAME[0]}")
            error_code=2
            error_code_array[2]=1
        fi 
    else 
        log "NOTICE" "/etc/httpd/conf/httpd.conf 설정파일이 존재하지 않습니다."
        log "NOTICE" "U_38테스트 점검불가" 
        ((na_cnt+=1))
        na_items+=("${FUNCNAME[0]}")
        error_code=10 
        error_code_array[10]=1
    fi 

}







#========== 메인 ============

for num in {0..38}; do 

    func_name="U_$(printf '%02d' "$num")"
    error_code=0


    case $num in 
        2|10|35|38)
            for j in "${!error_code_array[@]}"; do
                error_code_array[$j]=0
            done
            ;;


        *)
            ;;
    esac

    if declare -f "$func_name" > /dev/null; then 

        $func_name
        if [ $error_code -eq 0 ]; then 
            audit_result+=("양호")
        elif [ $error_code -ge 10 ]; then 
            audit_result+=("경고")
        else 
            audit_result+=("취약")
        fi 


        if [ $error_code -ne 0 ]; then 
            if [ $error_code -lt 10 ]; then 
                error_code_list+=("$error_code")
            case $num in
                2|10|35|38)
                    error_codes=()
                    for idx in "${!error_code_array[@]}"; do
                        if [ "${error_code_array[$idx]}" -eq 1 ]; then 
                            error_codes+=("$idx")
                        fi 
                    done 
                    error_code_dict["$func_name"]="${error_codes[*]}" 

                    ;;
            esac
            fi
        fi 
    fi 
done 


