# SDVX Random Select

레벨 17–20 채보 데이터를 자동 수집하고, 선택한 레벨에서 중복 없이 무작위 추천하는 독립 정적 페이지입니다. 기존 `sdvx` 파일과 연결되거나 이를 수정하지 않습니다.

## 데이터 갱신

```powershell
python sdvx/recommend_auto/scripts/update_sdvx_data.py
python sdvx/recommend_auto/scripts/validate_data.py
```

크롤러는 `robots.txt`를 먼저 확인한 다음 레벨별 정렬 페이지를 각각 한 번 요청합니다. 현재 사이트는 최종 곡 `<div>`를 원본 HTML에 직접 포함하지 않고 곡별 스크립트 선언으로 렌더링하므로, 선언에 포함된 곡 코드·채보 난이도와 인접 HTML 주석의 제목을 매칭합니다. 링크는 사이트 규칙인 `/{세대}/{곡 코드}{난이도 소문자}.htm`으로 생성합니다.

네 페이지 중 하나라도 요청 또는 파싱에 실패하거나, 레벨 하나가 비어 있거나, 검증이 실패하면 기존 JSON을 교체하지 않습니다. 기존 곡 배열과 같으면 `generatedAt`도 바꾸지 않아 불필요한 커밋이 생기지 않습니다. 빈 값, `#`, `javascript:` 링크는 빈 문자열로 정규화하며 해당 곡은 유지됩니다.

## 로컬 실행

`fetch()`로 JSON을 읽으므로 `file://`로 직접 열지 말고 저장소 루트에서 정적 서버를 실행합니다.

```powershell
python -m http.server 8000
```

그 뒤 `http://localhost:8000/sdvx/recommend_auto/`를 엽니다.

## 테스트

```powershell
python -m unittest discover -s sdvx/recommend_auto/tests -v
```

GitHub Actions의 `Update SDVX song data` 워크플로는 매주 월요일 03:00 UTC에 실행되며 수동 실행도 지원합니다. JSON이 실제로 달라진 경우에만 기본 `GITHUB_TOKEN`으로 데이터 파일 하나를 커밋합니다.

## 데이터 형식

루트 객체에는 `generatedAt`, 원본 페이지 목록, 전체/레벨별 개수와 `songs` 배열이 들어갑니다. 곡 레코드는 다음 형태입니다.

```json
{
  "title": "곡 제목",
  "level": 17,
  "difficulty": "M",
  "url": "https://sdvx.in/07/07068m.htm"
}
```

링크가 없는 곡은 `url`이 `""`이며 추천 대상에는 그대로 포함됩니다. 프론트엔드에서는 링크 대신 비활성화된 `링크 없음` 표시를 사용합니다.
