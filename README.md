# vault-mTLS
참고 자료 : https://github.com/Great-Stone/vault-mtls-demo

실습 velog : https://velog.io/@gweowe/Vault-pki를-활용한-mTLS-구현-MacOS


## mTLS란

### 1. TLS 정의


TLS는 네트워크 통신에서 데이터 보안을 위한 프로토콜이며, 국제 인터넷 표준화 기구(IETF) 표준으로 지정되어 있습니다.


- 기밀성 : 데이터를 암호화하여 제3자가 중간에서 데이터를 볼 수 없도록 합니다. 대칭키 암호화 방식으로 데이터를 암호화하고, 공개키 암호화 방식으로 대칭키를 교환합니다.
- 무결성 : 데이터가 중간에서 변조되지 않도록 보호하고 메시지 인증 코드(MAC)를 사용하여 데이터가 변경되지 않았음을 검증합니다.
- 인증 : 클라이언트와 서버가 서로를 인증하여 상호 신뢰 관계를 형성하고 X.509 인증서를 사용하여 서버와 클라이언트를 인증합니다. 인증서는 인증 기관(CA)에서 발급되며, 인증서에는 발급자 정보, 공개키, 서버 또는 클라이언트의 식별 정보 등이 포함됩니다.



![img](https://raw.githubusercontent.com/gweowe/Image-Server/main/images/mtls.png)

| 프로토콜           | 설명                                                         |
| ------------------ | ------------------------------------------------------------ |
| Handshake          | 클라이언트와 서버 간의 연결을 맺기 위한 3-way handshake 과정으로, SYN, SYN-ACK, ACK 패킷을 주고받아 연결을 설정 |
| Change Cipher Spec | TLS 핸드셰이크 과정에서 서로 약속한 대칭키 암호화 방식으로 암호화된 통신을 시작하기 전에, 클라이언트와 서버가 암호화 방식 변경을 완료했음을 나타내는 프로토콜 |
| Alert              | TLS 연결에서 발생한 오류 상황을 전송하는 프로토콜로, 오류 유형과 심각도 등의 정보를 포함하여 상대방에게 전달 |
| Application Data   | TLS 핸드셰이크 프로토콜을 통해 암호화된 통신에서 실제로 전달되는 애플리케이션 데이터 |
| Record             | TLS 핸드셰이크 프로토콜을 통해 암호화, 복호화, 무결성 검증 등을 수행 |



### 2. mTLS 정의


mutual Transport Layer Security의 약자로, 상호 인증된 SSL/TLS 연결을 구성하기 위한 프로토콜 입니다. 일반적으로 SSL/TLS을 사용하면 클라이언트는 서버에 대하여 인증서를 통해 검증하지만, 서버는 클라이언트에 대하여 인증서를 검증하지 않아 서버와 클라이언트 간의 단방향 인증만을 지원하는데, 이러한 경우에는 서버 측에서는 클라이언트의 신원을 확인할 수 없으므로 보안 상의 문제가 발생할 수도 있습니다. mTLS는 이러한 문제를 해결하기 위해, 클라이언트가 서버의 인증서를 검증하고, 서버는 클라이언트의 인증서를 검증하는 양방향 인증 방식을 제공하여 서버와 클라이언트 간의 상호 신뢰가 확립되고, 서로의 신원을 확인할 수 있습니다.






## Vault 실행 및 환경 구축

실습 Github에서 clone을 받아와서 실습을 진행합니다.

### 1. 개발 서버 실행


```bash
vault server -dev
```

##### Output :

```
WARNING! dev mode is enabled! In this mode, Vault runs entirely in-memory
and starts unsealed with a single unseal key. The root token is already
authenticated to the CLI, so you can immediately begin using Vault.

You may need to set the following environment variables:

    $ export VAULT_ADDR='http://127.0.0.1:8200'

The unseal key and root token are displayed below in case you want to
seal/unseal the Vault or re-authenticate.

Unseal Key: W/BcMhzReZB/+klCIp3EP0PQQNeXxsfi7aZ7D856KGo=
Root Token: hvs.nYoFXpxJqBlQSrKsgMEyWZkX

Development mode should NOT be used in production installations!
```

Vault의 `-dev` 플래그를 사용하여 개발 서버를 실행합니다.



### 2. Vault 주소 지정


```bash
export vault_ADDR=http://127.0.0.1:8200
```

환경변수로 Vault 서버가 실행중인 IP 주소를 지정합니다.



### 3. Root Token으로 로그인


```bash
vault login
```

##### Output :

```
Token (will be hidden): [Root Token]
```

첫 번째 작업에서 Output으로 출력된 Root Token의 값을 입력하여 로그인합니다.






## pki를 활용하여 서버 인증서 생성

Vault의 Secret Engine중 하나인 pki의 기능을 활용하여 인증서를 생성합니다. cert 폴더 안에서 진행하셔야 원활하게 따라오실 수 있습니다.

### 1. pki 활성화


```bash
vault secrets enable pki
```

-  `-path` 플래그를 사용하여 Secret Engine의 이름을 변경할 수 있습니다.



### 2. default MAX_TTL 변경


```bash
vault secrets tune -max-lease-ttl=87600h pki
```

테스트를 위해 pki로 생성하는 인증서의 TTL을 10년으로 변경합니다.



### 3. Root CA 생성


```bash
vault write pki/root/generate/internal \
    key_bits=2048 \
    private_key_format=pem \
    signature_bits=256 \
    country=KR \
    province=Gyeonggi \
    locality=Seongnam \
    organization=COMPANY \
    ou=DEV \
    common_name=server.com \
    ttl=87600h
```

Root CA 인증서를 생성할 때 필요한 값들을 지정해야하며, 명령어에 대한 설명은 아래와 같습니다.

- key_bits : 공개키와 개인키의 크기를 비트 단위로 지정
- private_key_format : 개인키를 생성하거나 저장할 때 사용되는 형식 지정
- signature_bits : 전자 서명을 생성할 때 사용되는 개인키의 크기를 비트 단위로 지정 (key_bit와는 다르게 개인 키만 지정)
- country : 국가 코드
- province : 국가 내의 지리적 단위로 나누어진 지역 정보 (경기도, 서울특별시 등)
- locality : 사용자가 위치한 도시 또는 시 정보 (성남, 대전 등)
- organization : 인증서를 발급 받는 조직 또는 회사의 이름
- ou : 조직 내에서 인증서를 발급 받는 특정 부서, 그룹 또는 단위
- common_name : 인증서가 발급되는 도메인 이름
- ttl : 발급되는 인증서의 유효기간

Root CA를 발급 받으면 certificate와 issuing_ca 총 2개가 발급되는데 이 실습에서는 Intermediate CA를 따로 지정하지 않았기 때문에 2개의 값이 같습니다.

certificate를 `ca.crt` 파일로 저장합니다.



### 4. CRL(Certificate Revocation List)의 Endpoint 작성


```bash
vault write pki/config/urls \
    issuing_certificates="http://127.0.0.1:8200/v1/pki/ca" \
    crl_distribution_points="http://127.0.0.1:8200/v1/pki/crl"
```

##### Output :

```
Key                        Value
---                        -----
crl_distribution_points    [http://127.0.0.1:8200/v1/pki/crl]
enable_templating          false
issuing_certificates       [http://127.0.0.1:8200/v1/pki/ca]
ocsp_servers               []
```

##### 

인증서가 유효한 인증서인지 검증하기 위해서 CRL Endpoint를 작성합니다.

- issuing_certificates : 인증서 발급을 담당하는 CA 인증서의 위치 지정
- crl_distribution_points : CRL의 배포 위치 지정



### 5. pki Role 생성


```bash
vault write pki/roles/server-dot-com \
    allowed_domains=server.com \
    allow_subdomains=true
```

Root CA를 통해 생성되는 하위 인증서를 만들기 위한 Role을 설정합니다.

- allowed_domains : 인증서를 발급받을 수 있는 도메인 지정
- allow_subdomains : 지정된 도메인의 하위 도메인에서도 인증서 발급을 가능하게 할 것인가에 대한 설정



### 6. 서버 인증서 발급


```bash
vault write pki/issue/server-dot-com \
    common_name=gweowe.server.com
```

`common_name`에 인증서의 주체가 되는 Domain을 입력합니다.

인증서를 발급할 경우 ca_chain, certificate, issuing_ca, private_key 4개가 발급됩니다.

- ca_chain : Root CA를 포함한 인증서 체인
- certificate : 인증서의 공개키와 서버의 정보
- issuing_ca : 인증서를 발급한 Intermediate CA의 인증서
- private_key : 인증서의 개인키 정보


certificate를 `server.crt` 파일로 저장하고 private_key를 `server.key` 파일로 저장합니다.




## mTLS 테스트

서버 인증서를 사용하여 클라이언트와 서버를 서로 인증하는 테스트를 수행합니다.


### 1. 사전 준비 사항

##### 1. python 버전을 확인합니다.

```bash
python3 --version
Python 3.8.10
```

python이 설치되어있지 않으면, 설치해주세요.

##### 2. pip 버전을 확인합니다.

```bash
pip3 --version
pip 21.2.4
```

pip가 설치되어있지 않으면, 설치해주세요.

##### 3. flask를 설치합니다.

```bash
pip3 install requests flask
```

pip를 이용하여, flask를 설치해주세요.

##### 4. host 파일을 설정합니다.

##### /etc/hosts

```
127.0.0.1 localhost gweowe.server.com
```

`gweowe.server.com`을 추가해줍니다.



### 2. mTLS 애플리케이션 실행

##### main.py


```
# -------------------- 생략 --------------------

if __name__ == "__main__":
    app.debug = True
    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH, cafile='../cert/ca.crt')
    ssl_context.load_cert_chain(certfile=f'../cert/server.crt', keyfile=f'../cert/server.key')
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    app.run(host="0.0.0.0", port=8443, ssl_context=ssl_context, use_reloader=True, extra_files=[f'../cert/server.crt'])
```

코드에 대한 주요 설정은 아래와 같습니다.

- ssl.create_default_context : Root CA 지정
- ssl_context.load_cert_chain : 인증서와 개인키를 합쳐서 지정
- ssl_context.verify_mode : 애플리케이션과 클라이언트 양측에 대한 검증을 수행 (mTLS의 역할 수행)
- app.run : Vault Agent를 통해 인증서가 변경될 경우, 재실행 되도록 구성


```bash
python3 main.py
```

python 코드로 짜여진 애플리케이션을 실행합니다.



### 3. curl을 사용해서 검증

curl 명령어를 사용하여 애플리케이션에 요청을 보냅니다.


```bash
curl  https://gweowe.server.com:8443
```

##### Output :

```
curl: (60) SSL certificate problem: self signed certificate in certificate chain
More details here: https://curl.haxx.se/docs/sslcerts.html

curl failed to verify the legitimacy of the server and therefore could not
establish a secure connection to it. To learn more about this situation and
how to fix it, please visit the web page mentioned above.
```

하지만 현재 애플리케이션은 상호간의 인증서를 요구하고 있기 때문에 에러가 발생합니다. `--insecure	` 플래그를 추가하여 클라이언트 측에서 인증서 검증을 받지 않도록 해봅시다.


```bash
curl --insecure https://gweowe.server.com:8443
```

##### Output :

```
curl: (35) LibreSSL/3.3.6: error:1401E410:SSL routines:CONNECT_CR_FINISHED:sslv3 alert handshake failure
```

클라이언트 측에서 애플리케이션에 대한 인증서 검증을 받지 않는다고 해도 애플리케이션은 클라이언트에게 인증서를 요구하기 때문에 에러가 발생합니다. 그러므로 `--cacert`, `--key`, `--cert` 플래그를 추가하여 애플리케이션에 인증서를 제출합니다.


```bash
curl --cacert ca.crt --key server.key --cert server.crt https://gweowe.server.com:8443 
```

##### Output :

```
Hello World!%
```

상호간의 인증이 완료되어 제대로 출력되는 것을 확인하실 수 있습니다.




## Vault Agent를 이용하여 자동 갱신

agent 폴더 안에서 진행하셔야 원활하게 따라오실 수 있습니다.

### 1. Agent에게 부여할 권한 생성


```bash
vault policy write pki_agent - << EOF
path "sys/mounts" {
  capabilities = [ "read", "list" ]
}
path "sys/mounts/*" {
  capabilities = [ "create", "read", "update", "delete", "list" ]
}
path "pki*" {
  capabilities = [ "create", "read", "update", "delete", "list", "sudo" ]
}
EOF
```

Vault Agent가 pki에 대한 자동 갱신 작업을 수행할 수 있도록 권한을 생성합니다.

- 'path "sys/mounts"' : 현재 마운트된 백엔드 엔진의 정보를 제공하기 위한 경로
- 'path "sys/mounts/*"' : 시스템의 마운트 포인트를 관리하기 위한 경로

- 'path "pki*"' :  pki를 관리하기 위한 경로



### 2. Agent가 사용할 인증 수단 생성


```bash
vault auth enable approle
```


```bash
vault write auth/approle/role/pki-agent \
    secret_id_ttl=120m \
    token_ttl=60m \
    token_max_tll=120m \
    policies="pki_agent"
```


```bash
vault read -field=role_id auth/approle/role/pki-agent/role-id > roleid
```


```bash
vault write -f -field=secret_id auth/approle/role/pki-agent/secret-id > secretid
```

Vault Agent가 Vault에 인증하기 위해 role_id와 secret_id를 생성하여 추출합니다.

secret_id는 role_id와 달리 TTL이 존재하기 때문에 시간에 따라 변경될 수도 있으며, Vault Agent를 실행하여 사용할 경우, 파일이 사라지기 때문에 매 번 생성해야 합니다.

### 3. Vault Agent 템플릿 확인

##### vault_agent.hcl


```
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
  source      = "ca.tpl"
  destination = "../cert/ca.crt"
}

# -------------------- 생략 --------------------
```

Vault Agent를 사용하기 위한 파일에 대한 설명은 아래와 같습니다.

- method : Vault Agent가 Vault에 인증할 방식을 구성
- sink : Vault Agent가 `template`의 `source`에서 가져온 시크릿 데이터를 처리하기 위한 일련의 작업을 수행하는 서비스 또는 애플리케이션을 지정
- source : 저장된 시크릿 데이터를 읽어들이기 위한 경로
- destination : 시크릿 데이터를 적용할 대상 경로

##### ca.tpl


```
{{- /* ca.tpl */ -}}
{{ with secret "pki/issue/server-dot-com" "common_name=gweowe.server.com" "ttl=5m" }}
{{ .Data.issuing_ca }}{{ end }}
```

시크릿 데이터에 대한 설명은 아래와 같습니다.

- with secret : 인증서를 발급하기 위한 pki role을 지정
- common_name : 인증서의 주체가 될 Domain을 지정
- ttl : 인증서의 유효기간 지정



### 4. Vault Agent 실행


```bash
vault agent -config=vault_agent.hcl -log-level=debug
```

##### output :

```
2023-04-04T06:43:12.683Z [DEBUG] (runner) checking template feedf705af52a05c195d09088f4f0a95
2023-04-04T06:43:12.684Z [DEBUG] (runner) rendering "ca.tpl" => "../cert/ca.crt"
2023-04-04T06:43:12.686Z [INFO] (runner) rendered "ca.tpl" => "../cert/ca.crt"
2023-04-04T06:43:12.686Z [DEBUG] (runner) checking template 3b3d9d5fa3dd91f5ce0993dae1d9fcfa
2023-04-04T06:43:12.687Z [DEBUG] (runner) rendering "cert.tpl" => "../cert/server.crt"
2023-04-04T06:43:12.688Z [INFO] (runner) rendered "cert.tpl" => "../cert/server.crt"
2023-04-04T06:43:12.688Z [DEBUG] (runner) checking template 32df92b4a187d27c7428feb111926ee4
2023-04-04T06:43:12.688Z [DEBUG] (runner) rendering "key.tpl" => "../cert/server.key"
2023-04-04T06:43:12.690Z [INFO] (runner) rendered "key.tpl" => "../cert/server.key"

# -------------------- 생략 --------------------

2023-04-04T01:38:41.187Z [DEBUG] (runner) all templates rendered
```

Vault Agent 작업이 끝나면 인증서가 새로 발급되어 기존의 파일이 대체됩니다.

Vault Agent로 발급받은 인증서로 테스트를 해보면 성공적으로 인증이 되지만, 지정해놓은 TTL인 5분이 지나면 인증서가 만료됩니다.
