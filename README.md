# vault-mTLS
python 어플리케이션 및 자료 출처 : https://github.com/Great-Stone/vault-mtls-demo

vault pki를 활용한 mTLS 사용 가이드
(Dev 환경을 기준으로 구축)




## 1. vault 실행



### 1-1. dev 서버로 실행


```
vault server -dev
```



## 2. vault 사용 환경 구축



### 2-1. vault 주소 지정


```
export vault_ADDR=http://127.0.0.1:8200
```



### 2-2. Root Ten으로 로그인 하기


```
vault login

Token (will be hidden): [Root_Token]
```
또는
```
export VAULT_TOKEN=[Root_Token]
```




## 3. pki를 활용하여 'service-a', 'service-b' 인증서 생성



### 3-1. pki 활성화


```
vault secrets enable pki
```



### 3-2. default MAX_TTL 변경


```
vault secrets tune -max-lease-ttl=876006h pki
```


10년짜리 인증서를 생성하기 위해서 default MAX_TTL을 10년으로 변경



### 3-3. Root CA 생성


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



### 3-4. CRL(Certificate Revocation List)의 Endpoint 작성


```
vault write pki/config/urls \
    issuing_certificates="http://127.0.0.1:8200/v1/pki/ca" \
    crl_distribution_points="http://127.0.0.1:8200/v1/pki/crl"
```
- issuing_certificates : 인증서 발급을 담당하는 CA 인증서의 위치 지정
- crl_distribution_points : CRL의 배포 위치 지정


인증서의 폐지 여부를 확인하기 위해 클라이언트는 CRL 파일을 다운로드하고, 해당 CRL 파일의 서명이 유효한지 확인하기 위해 issuing_certificates 옵션에 지정된 CA 인증서를 다운로드하여 검증함
또한 crl_distribution_points 옵션에 지정된 위치에서 CRL을 확인하고, CRL에 해당하는 인증서가 존재하는 경우 해당 인증서를 폐지함



### 3-5. pki Role 생성


```
vault write pki/roles/example-dot-com \
    allowed_domains=example.com \
    allow_subdomains=true
```
- allowed_domains : 인증서를 발급받을 수 있는 도메인 지정
- allow_subdomains : 지정된 도메인의 하위 도메인에서도 인증서 발급을 가능하게 할 것인가에 대한 설정



### 3-6. 'service-a' 인증서 발급


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



### 3-7. 'service-b' 인증서 발급


```
vault write pki/issue/example-dot-com \
    common_name=service-b.example.com
```


'certificate'를 'service-b.crt'파일로 저장하고 private_key를 'service-b.key'파일로 저장




## 4. mTLS 테스트



### 4-1. 사전 준비 사항


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
#sudo vi /etc/hosts

127.0.0.1 service-a.example.com service-b.example.com
```



### 4-2. mTLS 어플리케이션 실행 


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


```
python3 main.py
```



### 4-3. curl을 사용해서 검증하기


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
curl에 root CA, key, cert 파일을 어플리케이션에 제공하여 mTLS에 대한 테스트 완료
