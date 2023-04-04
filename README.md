# vault-mTLS
python 어플리케이션 및 자료 출처 : https://github.com/Great-Stone/vault-mtls-demo

vault pki를 활용한 mTLS 사용 가이드
(Dev 환경을 기준으로 구축)



## 0. mTLS



### 0-1. TLS의 정의


네트워크 통신에서 데이터 보안을 위한 프로토콜로, 국제 인터넷 표준화 기구(IETF)에서 표준으로 인정받음


- 기밀성 : 데이터를 암호화하여 제3자가 중간에서 데이터를 볼 수 없도록 하고 대칭키 암호화 방식으로 데이터를 암호화하고, 공개키 암호화 방식으로 대칭키를 교환함
- 무결성 : 데이터가 중간에서 변조되지 않도록 보호하고 메시지 인증 코드(MAC)를 사용하여 데이터가 변경되지 않았음을 검증함
- 인증 : 클라이언트와 서버가 서로를 인증하여 상호 신뢰 관계를 형성하고 X.509 인증서를 사용하여 서버와 클라이언트를 인증
인증서는 인증 기관(CA)에서 발급되며, 인증서에는 발급자 정보, 공개키, 서버 또는 클라이언트의 식별 정보 등이 포함됨

|프로토콜|설명|
|------|---|
|Handshake|클라이언트와 서버 간의 연결을 맺기 위한 3-way handshake 과정으로, SYN, SYN-ACK, ACK 패킷을 주고받아 연결을 설정|
|Change Cipher Spec|TLS 핸드셰이크 과정에서 서로 약속한 대칭키 암호화 방식으로 암호화된 통신을 시작하기 전에, 클라이언트와 서버가 암호화 방식 변경을 완료했음을 나타내는 프로토콜|
|Alert|TLS 연결에서 발생한 오류 상황을 전송하는 프로토콜로, 오류 유형과 심각도 등의 정보를 포함하여 상대방에게 전달|
|Application Data|TLS 핸드셰이크 프로토콜을 통해 암호화된 통신에서 실제로 전달되는 애플리케이션 데이터|
|Record|TLS 핸드셰이크 프로토콜을 통해 암호화, 복호화, 무결성 검증 등을 수행|


<p align="center">
  <img
    src="https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FcRsBaG%2FbtqE4DyXDqG%2FK6BxQuKq8CwVcjKs6WgpMK%2Fimg.png"
  />
</p>


### 0-2. mTLS 정의


mutual Transport Layer Security의 약자로, 상호 인증된 SSL/TLS 연결을 구성하기 위한 프로토콜 \
일반적으로 SSL/TLS을 사용하면 클라이언트는 서버에 대하여 인증서를 통해 검증하지만, 서버는 클라이언트에 대하여 인증서를 검증하지 않아 서버와 클라이언트 간의 단방향 인증만을 지원함 \
이러한 경우에는 서버 측에서는 클라이언트의 신원을 확인할 수 없으므로 보안 상의 문제가 발생할 수도 있음 \
mTLS는 이러한 문제를 해결하기 위해, 클라이언트가 서버의 인증서를 검증하고, 서버는 클라이언트의 인증서를 검증하는 양방향 인증 방식을 제공하여 서버와 클라이언트 간의 상호 신뢰가 확립되고, 서로의 신원을 확인할 수 있음



### 0-2. TLS Handshake 과정
<p align="center">
  <img
    src="https://i.postimg.cc/2SbhXTSk/2023-04-04-1-35-01.png"
  />
</p>



### 0-3. mTLS Handshake 과정
<p align="center">
  <img
    src="https://raw.githubusercontent.com/Great-Stone/images/master/uPic/image-20230320091236622.png"
  />
</p>




## 1. vault 실행 및 환경 구축



### 1-1. dev 서버로 실행


```
vault server -dev
```



### 1-2. vault 주소 지정


```
export vault_ADDR=http://127.0.0.1:8200
```



### 1-3. Root Token으로 로그인 하기


```
vault login

Token (will be hidden): [Root_Token]
```
또는
```
export VAULT_TOKEN=[Root_Token]
```




## 2. pki를 활용하여 'service-a', 'service-b' 인증서 생성
클라이언트와 서버가 서로를 인증할 수 있도록 인증서를 2개 생성


### 2-1. pki 활성화


```
vault secrets enable pki
```



### 2-2. default MAX_TTL 변경


```
vault secrets tune -max-lease-ttl=876006h pki
```



### 2-3. Root CA 생성


```
vault write pki/root/generate/internal \
    key_bits=2048 \
    private_key_format=pem \
    signature_bits=256 \
    country=KR \
    province=Gyeonggi \
    locality=Seongnam \
    organization=COMPANY \
    ou=DEV \
    common_name=example.com \
    ttl=87600h
```
- key_bits : 공개 키와 개인 키의 크기를 비트 단위로 지정
- private_key_format : 개인 키를 생성하거나 저장할 때 사용되는 형식 지정
- signature_bits : 전자 서명을 생성할 때 사용되는 개인키의 크기를 비트 단위로 지정하는 것 (key_bit와는 다르게 개인 키만 지정함)
- country : 두 자리 ISO 3166-1 alpha-2 국가 코드
- province : 국가 내의 지리적 단위로 나누어진 지역 정보 (경기도, 충청도, 서울특별시 등)
- locality : 사용자가 위치한 도시 또는 시 정보 (성남, 광주 등)
- organization : 인증서를 발급 받는 조직 또는 회사의 이름
- ou : 조직 내에서 인증서를 발급 받는 특정 부서, 그룹 또는 단위
- common_name : 인증서가 발급되는 도메인 이름
- ttl : 발급되는 인증서의 유효기간


'certificate'와 'issuing_ca' 2개가 발급되는데 이 예제에서는 Intermediate CA를 따로 지정하지 않아 2개의 값이 같음
둘중 아무거나 복사하여 'ca.crt'로 저장



### 2-4. CRL(Certificate Revocation List)의 Endpoint 작성


```
vault write pki/config/urls \
    issuing_certificates="http://127.0.0.1:8200/v1/pki/ca" \
    crl_distribution_points="http://127.0.0.1:8200/v1/pki/crl"
```
- issuing_certificates : 인증서 발급을 담당하는 CA 인증서의 위치 지정
- crl_distribution_points : CRL의 배포 위치 지정



### 2-5. pki Role 생성


```
vault write pki/roles/example-dot-com \
    allowed_domains=example.com \
    allow_subdomains=true
```
- allowed_domains : 인증서를 발급받을 수 있는 도메인 지정
- allow_subdomains : 지정된 도메인의 하위 도메인에서도 인증서 발급을 가능하게 할 것인가에 대한 설정



### 2-6. 'service-a' 인증서 발급


```
vault write pki/issue/example-dot-com \
    common_name=service-a.example.com
```
- common_name : 인증서의 주체를 지정

'ca_chain', 'certificate', 'issuing_ca', 'private_key' 4개가 발급됨
- ca_chain : Root CA를 포함한 인증서 체인
- certificate : 인증서의 공개키와 서버의 정보
- issuing_ca : 인증서를 발급한 Intermediate CA의 인증서 (이 예제의 경우 Intermediate CA를 따로 지정하지 않아 Root CA와 값이 같음)
- private_key : 인증서의 개인키 정보


'certificate'를 'service-a.crt'파일로 저장하고 private_key를 'service-a.key'파일로 저장



### 2-7. 'service-b' 인증서 발급


```
vault write pki/issue/example-dot-com \
    common_name=service-b.example.com
```


'certificate'를 'service-b.crt'파일로 저장하고 private_key를 'service-b.key'파일로 저장




## 3. mTLS 테스트
'service-a' 인증서와 'service-b' 인증서를 사용하여 클라이언트와 서버를 서로 인증하는 테스트 수행


### 3-1. 사전 준비 사항


python 버전 확인
```
python3 --version
Python 3.8.10
```


pip 버전 확인
```
pip --version
pip 20.0.2
```


flask 설치
```
pip install requests flask
```


hostfile 설정
```
# hosts

127.0.0.1 service-b.example.com
```



### 3-2. mTLS 어플리케이션 실행 


```
# cd python_service
# main.py
# -------------------- 생략 --------------------

if __name__ == "__main__":
    app.debug = True
    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH, cafile='../cert/ca.crt')
    ssl_context.load_cert_chain(certfile=f'../cert/{src}.crt', keyfile=f'../cert/{src}.key', password='')
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    app.run(host="0.0.0.0", port=src_port, ssl_context=ssl_context, use_reloader=True, extra_files=[f'../cert/{src}.crt'])
```
- ssl.create_default_context : 어플리케이션에 삽입 시킬 인증서의 root CA 파일 지정
- ssl_context.load_cert_chain : cert와 key를 chain으로 만듦
- ssl_context.verify_mode : 어플리케이션과 클라이언트 양측 인증서에 대한 검증을 수행 (mTLS의 역할 수행)
- app.run : vault Agent를 통해 인증서가 변경될 경우, flask가 재실행 되도록 구성


```
python3 main.py
```



### 3-3. curl을 사용해서 검증하기


```
curl  https://service-b.example.com:8443
```
output :
```
curl: (60) SSL certificate problem: self signed certificate in certificate chain
More details here: https://curl.haxx.se/docs/sslcerts.html

curl failed to verify the legitimacy of the server and therefore could not
establish a secure connection to it. To learn more about this situation and
how to fix it, please visit the web page mentioned above.
```
클라이언트에서 인증서를 검증할 수 없기 때문에 연결이 실패


```
curl --insecure https://service-b.example.com:8443
```
- --insecure : 인증서 검증을 수행하지 않도록 하는 옵션
output :
```
curl: (55) OpenSSL SSL_write: Connection reset by peer, errno 104
```
클라이언트 측에서 인증서 검증을 무시해도 어플리케이션은 인증서를 요구하기 때문에 에러 발생


```
curl --cacert ca.crt --key service-b.key --cert service-b.crt https://service-b.example.com:8443 
```
output :
```
Hello from "service-b"%
```
root CA, key, cert 파일을 어플리케이션에 제공하여 mTLS 인증 성공



## 4. vault Agent를 이용하여 자동 갱신


### 4-1. Agent에게 부여할 권한 생성


```
vault policy write pki_agent - << EOF
path "sys/mounts/*" {
  capabilities = [ "create", "read", "update", "delete", "list" ]
}
path "sys/mounts" {
  capabilities = [ "read", "list" ]
}
path "pki*" {
  capabilities = [ "create", "read", "update", "delete", "list", "sudo" ]
}
EOF
```
- 'path "sys/mounts/*"' : 시스템의 마운트 포인트를 관리하기 위한 경로
- 'path "sys/mounts"' : 현재 마운트된 백엔드 엔진의 정보를 제공하기 위한 경로
- 'path "pki*"' :  pki와 관련된 모든 경로에 대해 관리하기 위한 경로


vault Agent가 pki를 자동 갱신 작업을 수행할 수 있도록 권한을 부여



### 4-2. Agent가 사용할 인증 수단 생성


```
vault auth enable approle
```


```
vault write auth/approle/role/pki-agent \
    secret_id_ttl=120m \
    token_ttl=60m \
    token_max_tll=120m \
    policies="pki_agent"
```


```
vault read -field=role_id auth/approle/role/pki-agent/role-id > roleid
```


```
vault write -f -field=secret_id auth/approle/role/pki-agent/secret-id > secretid
```


vault Agent가 인증하기 위해 roldid와 secretid를 따로 저장 (secretid는 roleid와 달리 TTL이 존재하기 때문에 시간에 따라 변경될 수도 있으며, vault Agent를 실행할 경우 파일이 사라짐)



### 4-3. vault Agent 템플릿 확인


```
# vault_agent.hcl

auto_auth {
  method  {
    type = "approle"
    config = {
      role_id_file_path = "roleid"
      secret_id_file_path = "secretid"
    }
  }

  sink {
    type = "file"
    config = {
      path = "/tmp/vault_agent"
    }
  }
}

# -------------------- 생략 --------------------

template {
  source      = "ca-a.tpl"
  destination = "../cert/ca.crt"
}

# -------------------- 생략 --------------------
```
- method : vault Agent가 인증할 방식을 구성
- sink : vault Agent가 template의 source에서 가져온 데이터를 처리하기 위한 일련의 작업을 수행하는 서비스 또는 애플리케이션을 지정
- source : 저장된 시크릿 데이터를 읽어들이기 위한 경로
- destination : 읽은 데이터를 적용할 대상 경로


```
# ca-a.tpl

{{- /* ca-a.tpl */ -}}
{{ with secret "pki/issue/example-dot-com" "common_name=service-a.example.com" "ttl=2m" }}
{{ .Data.issuing_ca }}{{ end }}
```
- with secret : 데이터를 가져오기 위한 endpoint 지정
- common_name : 인증서의 주체를 지정
- ttl : 인증서의 유효기간 지정 (테스트를 위해 짧게 지정함)



### 4-4. vault Agent 실행


```
vault agent -config=vault_agent.hcl -log-level=debug
```

output :
```
2023-04-04T01:38:41.182Z [DEBUG] (runner) checking template 4903c0854a0a6bdcd74cf9219422748a
2023-04-04T01:38:41.183Z [DEBUG] (runner) rendering "ca-a.tpl" => "../cert/ca.crt"
2023-04-04T01:38:41.183Z [DEBUG] (runner) checking template a04612e63b9a03a45ef968a8984a23db
2023-04-04T01:38:41.183Z [DEBUG] (runner) rendering "cert-a.tpl" => "../cert/service-a.crt"
2023-04-04T01:38:41.183Z [DEBUG] (runner) checking template 850589d81f7afe64c7c5a0a8440c8569
2023-04-04T01:38:41.183Z [DEBUG] (runner) rendering "key-a.tpl" => "../cert/service-a.key"
2023-04-04T01:38:41.184Z [DEBUG] (runner) checking template 60e7f2683d2c76a501eb54879bf89ad2
2023-04-04T01:38:41.184Z [DEBUG] (runner) rendering "cert-b.tpl" => "../cert/service-b.crt"
2023-04-04T01:38:41.185Z [INFO] (runner) rendered "cert-b.tpl" => "../cert/service-b.crt"
2023-04-04T01:38:41.185Z [DEBUG] (runner) checking template 1fb22b9f15857b7eeb0b68a3c9ac6d20
2023-04-04T01:38:41.185Z [DEBUG] (runner) rendering "key-b.tpl" => "../cert/service-b.key"
2023-04-04T01:38:41.187Z [INFO] (runner) rendered "key-b.tpl" => "../cert/service-b.key"

# -------------------- 생략 --------------------

2023-04-04T01:38:41.187Z [DEBUG] (runner) all templates rendered
```
vault Agent 작업이 끝나면 인증서가 새로 발급되어 교체 완료
