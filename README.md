# vault-mTLS

Vault PKI를 활용한 인증서 생성 + mTLS 테스트 가이드
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
- crl_distribution_points : 인증서 발급을 담당하는 CA 인증서의 위치를 가리키는 URI 지정
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
미리 Role을 구성해 놓고 나중에 지정한 Role을 따르는 인증서를 발급



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
