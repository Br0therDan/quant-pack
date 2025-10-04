# 인증/인가 플로우


## NextAuth.js
```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Next.js (NextAuth)
    participant FastAPI
    participant Google OAuth

    %% Step 1: OAuth 시작
    User->>Browser: 클릭 "Google 로그인"
    Browser->>Next.js (NextAuth): 요청 /api/auth/signin
    Next.js->>Google OAuth: Redirect (OAuth URL with PKCE)

    %% Step 2: 인증 후 리디렉션
    Google OAuth-->>Next.js (NextAuth): Redirect with Auth Code
    Next.js->>Google OAuth: Token 교환 (Auth Code → Access Token)
    Google OAuth-->>Next.js: Access Token + User Info

    %% Step 3: 세션 생성
    Next.js->>Next.js: 세션 or JWT 생성
    Next.js-->>Browser: Set-Cookie: next-auth.session-token or JWT

    %% Step 4: API 호출 (인증됨)
    Browser->>FastAPI: 요청 Authorization: Bearer <NextAuth JWT>
    FastAPI->>FastAPI: JWT 검증 (e.g. issuer, signature, email)
```

### 구글
http://localhost:3000/api/oauth2/google/callback?
state=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJ1c2VyczpvYXV0aC1zdGF0ZSJ9.0htGWaINXB8i9pawAHpMpUcF8D4otF7CbPIsV4uwxSE&
code=4%2F0AVGzR1BRTxgz21JpiZEGxhOP6TPRGZ29C8X_Uwr61QRvVjKCue0Hf1ZF500z6IZ3-7JaCw&scope=email+profile+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+openid&authuser=0&hd=mysingle.io&prompt=consent
