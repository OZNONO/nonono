# SDVX 자동 갱신 추천기

기존 `sdvx/recommendtotal.html`의 사용 경험을 보존하면서 레벨 17–20 자동 갱신, 무중복 추천, 자켓, 검색과 결과 복사를 추가한 독립 페이지입니다. 기존 `sdvx` 파일은 읽기만 하며 수정하지 않습니다.

## 실행

GitHub Pages 같은 정적 서버에서는 별도 설정 없이 `index.html`을 열면 됩니다. 저장소 루트에서 로컬 서버를 실행할 수도 있습니다.

```powershell
python -m http.server 8000
```

그 뒤 `http://localhost:8000/sdvx/recommend_auto/`를 엽니다.

`index.html`을 `file://`로 직접 열 때 브라우저가 로컬 JSON `fetch()`를 차단하는 문제를 피하기 위해, 크롤러는 동일 내용의 `data/sdvx_songs.js`도 생성합니다. HTTP에서는 JSON을 우선 사용하고, 직접 열기 또는 JSON 로드 실패 시에만 이 사본을 사용합니다.

## 기존 페이지에서 보존한 동작

- 기본 추천 수 3곡
- 레벨 18만 기본 선택
- 로드 직후 날짜 시드로 정해지는 17·18·19 “오늘의 추천곡”
- 선택 레벨 없이 추첨하면 `Dyscontrolled galaxy!!`
- 추첨 뒤 안내 문구와 `재추첨` 버튼
- 검색, 사진 복사, 텍스트 복사
- 흰 배경, 중앙 제목, 작은 Bootstrap 계열 버튼과 단순한 결과 목록

텍스트 복사는 기존처럼 결과의 `곡 제목 (레벨)`을 한 줄씩 복사합니다. URL이나 `undefined`를 덧붙이지 않아 메신저와 메모장에 바로 붙여넣기 쉽습니다. Clipboard API가 없으면 기존 `execCommand` 방식으로 한 번 더 시도합니다. 사진 복사는 화면의 결과 행을 기준으로 로컬 자켓, 제목, 실제 채보 타입과 난이도를 2배 해상도 PNG에 함께 그립니다.

## 데이터 갱신

```powershell
python sdvx/recommend_auto/scripts/update_sdvx_data.py
python sdvx/recommend_auto/scripts/validate_data.py
```

크롤러는 `robots.txt`를 확인한 뒤 레벨별 정렬 페이지를 각각 한 번 요청합니다. 사이트가 최종 곡 `<div>`를 원본 HTML에 직접 넣지 않고 곡별 스크립트 선언으로 렌더링하므로, 선언의 곡 코드와 인접 주석의 제목을 매칭합니다. 처음 보는 곡만 해당 `sort.js`를 한 번 읽어 `MXM`, `GRV`, `INF`, `HVN`, `VVD`, `XCD`, `NBL` 등의 실제 채보 타입을 저장합니다.

레벨 페이지에 `18.3`, `19.1`처럼 실제 세부 난이도 구간이 명시된 채보는 그 값을 저장합니다. 해당 표기가 없는 이전 버전 채보에는 값을 추정하지 않고 정수 레벨을 사용합니다.

네 페이지 중 하나라도 실패하거나 레벨이 비거나 검증이 실패하면 기존 JSON을 교체하지 않습니다. 곡 배열이 같으면 생성 시각을 바꾸지 않아 불필요한 커밋도 만들지 않습니다. 빈 값, `#`, `javascript:` 링크는 빈 문자열로 정규화하되 곡은 유지합니다.

## 자켓 처리

곡별 상세 페이지가 불러오는 `/{세대}/js/{곡 코드}data.js`의 `JK{곡 코드}{난이도}` 변수를 여러 세대에서 확인해 원본 자켓 URL을 매칭합니다. 크롤러는 신규 또는 URL이 바뀐 이미지만 내려받아 `assets/jackets/{세대}_{곡코드}_{키}.webp`에 256×256, WebP quality 78로 저장합니다. 프론트엔드는 `jacketPath`의 로컬 상대경로만 표시하므로 방문할 때 sdvx.in에 이미지 요청을 보내지 않고 캔버스 복사에도 CORS 문제가 없습니다.

외부 URL 직접 표시는 저장소가 작지만 방문할 때마다 원본 서버 트래픽과 가용성·CORS의 영향을 받습니다. 로컬 WebP는 저장소가 약 33MB 늘어나는 대신 페이지 요청이 빠르고 안정적이며 원본 PNG보다 전송량이 작습니다. 현재 1,906개 중 원본이 404인 한 곡은 다운로드 실패가 전체 갱신을 막지 않으며 `NO IMAGE` fallback을 사용합니다. 기존 WebP는 다시 다운로드하지 않습니다.

현재 `robots.txt`는 필요한 경로를 허용하지만 이는 이미지 재배포 라이선스를 의미하지 않습니다. 공개 저장소와 GitHub Pages에서 자켓을 배포할 권한은 저장소 운영자가 별도로 확인해야 합니다.

개발 시 각 레벨의 처음·중간·마지막 곡을 실제 곡 데이터 스크립트 및 PNG 응답과 대조할 수 있습니다.

```powershell
python sdvx/recommend_auto/scripts/verify_jacket_samples.py
```

## 데이터 형식

```json
{
  "title": "BUBBLE RAVER",
  "level": 18,
  "difficulty": 18.4,
  "chartType": "NBL",
  "url": "https://sdvx.in/02/02139m.htm",
  "jacketPath": "assets/jackets/02_02139_m.webp",
  "sourceJacketUrl": "https://sdvx.in/02/jacket/02139m.png"
}
```

## 테스트와 자동화

```powershell
python -m unittest discover -s sdvx/recommend_auto/tests -v
```

GitHub Actions의 `Update SDVX song data`는 Pillow를 설치한 뒤 매주 월요일 03:00 UTC 및 수동 실행으로 동작합니다. JSON, file fallback 또는 로컬 자켓이 실제로 변경될 때만 기본 `GITHUB_TOKEN`으로 커밋합니다.
