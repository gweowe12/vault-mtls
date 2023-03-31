# Vault-mTLS
Vault를 활용한 mTLS 사용 가이드
(Dev 환경을 기준으로 구축)

### 1. Vault 실행
```
\\<!-- dev 서버로 실행 -->
vault server -dev
```

### 2. Vault 사용 환경 구축
```
\\<!-- 환경변수 설정 -->
export VAULT_ADDR=http://127.0.0.1:8200
```
```
\\<!-- 작업 가능한 Token으로 로그인 하기 -->
vault login
```
```
Token (will be hidden): [Root_Token]
```

### 3. PKI를 활용하여 인증서 생성
```
\\<!-- pki를 사용하기 위해 활성화 -->
vault secrets enable pki
```
