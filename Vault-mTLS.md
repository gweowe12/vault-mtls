# vault-mTLS

vault를 활용한 mTLS 사용 가이드
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
export vault_TOKEN=[Root_Token]
```

## 3. pki를 활용하여 인증서 생성

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

* 위 명령어를 입력할 경우 아래와 같은 output이 나옴
```
This mount hasn't configured any authority information access (AIA)
fields; this may make it harder for systems to find missing certificates
in the chain or to validate revocation status of certificates. Consider
updating /config/urls or the newly generated issuer with this information.
```
이는 AIA(Authority Information Access) 필드가 제대로 설정되지 않아 인증서 체인을 검증하는데 어려움을 겪을 수 있다는 것을 의미하는데 `pki/config/urls` Endpoint를 설정하면 해결됨

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
    allow_subdomains=true \
    max_ttl=72h
```
- allowed_domains : 인증서를 발급받을 수 있는 도메인 지정
- allow_subdomains : 지정된 도메인의 하위 도메인에서도 인증서 발급을 가능하게 할 것인가에 대한 설정
미리 Role을 구성해 놓고 나중에 지정한 Role을 따르는 인증서를 발급

### 3-6. 발급
```
vault write pki/issue/example-dot-com \
    common_name=service-a.example.com
```

* 아래와 같은 경고문이 발생한 이유
```
TTL "768h0m0s" is longer than permitted maxTTL "72h0m0s", so maxTTL is
  being used
```
pki에 대해 default MAX_TTL을 87600h으로 늘렸지만, pki Role을 설정할 때 MAX_TTL을 72h로 지정했기 때문에 default TTL인 768h이 MAX_TTL인 72h 넘기지 못하여 발생함

### 