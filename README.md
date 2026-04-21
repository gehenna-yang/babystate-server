# 👶 BabyState
아이의 소중한 일상을 기록하고 관리하는 서비스입니다.

## ⚙️ 실행 방법

### 1. 데이터베이스 실행
Docker가 설치된 환경에서 아래 명령어를 통해 PostgreSQL DB를 실행합니다.
\`\`\`bash
docker-compose up -d
\`\`\`

### 2. 백엔드 실행
Python 가상환경을 생성하고 의존성을 설치한 후 서버를 켭니다.
\`\`\`bash
pip install -r requirements.txt
uvicorn main:app --reload
\`\`\`

### 3. 프론트엔드 실행
새 터미널을 열고 프론트엔드 패키지를 설치한 후 Vite 서버를 켭니다.
\`\`\`bash
npm install
npm run dev
\`\`\`

### 4. 접속
브라우저를 열고 `http://localhost:5173` 으로 접속

