var songliststotal = new Array;
songliststotal = songlists18.concat(songlists19).concat(songlists17).concat(songlists20);
xi = songliststotal.length; // 곡 갯수
xxi.innerHTML = "전체 곡 수: "+ xi +"곡";

function input() {
  const songlistcheck = [];
  const linkcheck = []; // 링크를 저장할 새 배열 추가

  if (document.getElementById("checkbox1").checked) {
    songlistcheck.push(...songlists17);
    linkcheck.push(...links17); // 동일한 순서의 링크 추가
  }

  if (document.getElementById("checkbox2").checked) {
    songlistcheck.push(...songlists18);
    linkcheck.push(...links18); // 동일한 순서의 링크 추가
  }

  if (document.getElementById("checkbox3").checked) {
    songlistcheck.push(...songlists19);
    linkcheck.push(...links19); // 동일한 순서의 링크 추가
  }

  if (document.getElementById("checkbox4").checked) {
    songlistcheck.push(...songlists20);
    linkcheck.push(...links20); // 동일한 순서의 링크 추가
  }

  sival = songlistcheck.length;

  $("ul").empty();
  var howmany = document.getElementById("select1").value;
  if (sival === 0) {
    document.getElementById("ul").innerHTML = "Dyscontrolled galaxy!!";
  } else {
    for (i = 0; i < howmany; i++) {
      var index = Math.floor(Math.random() * (sival));
      var newDiv = document.createElement('div');
      newDiv.id = "result" + i;
      // 하이퍼링크 생성
      var newLink = document.createElement('a');
      newLink.href = linkcheck[index]; // 링크 참조
      newLink.textContent = songlistcheck[index]; // 텍스트 내용 설정
      newDiv.appendChild(newLink); // 하이퍼링크를 div에 추가
      document.getElementById("ul").appendChild(newDiv);
    }
  }
  message2.innerHTML = "마음에 들지 않는다면 재추첨 버튼을 눌러주세요";
  cc.innerHTML = "재추첨";
}

document.getElementById('copy-btn').addEventListener('click', function() {
  html2canvas(document.getElementById('ul')).then(canvas => {
    canvas.toBlob(function(blob) {
      navigator.clipboard.write([
        new ClipboardItem({'image/png': blob})
      ]);
    });
  });
});

document.getElementById('copyButton').addEventListener('click', function() {
  const ulContent = document.getElementById('ul').innerText;
  navigator.clipboard.writeText(ulContent).then(() => {
      alert('클립보드에 복사되었습니다!');
  }).catch(err => {
      console.error('복사 실패:', err);
  });
});

//이하 오늘의 추천곡
years17 = songlists17.length;
years18 = songlists18.length;
years19 = songlists19.length;
function seededRandom(seed, min, max) {
  // 시드를 사용하여 난수 생성
  const seedFunction = (seed) => {
      seed = (seed * 9301 + 49297) % 233280;
      return seed / 233280;
  };
  const random = seedFunction(seed);
  return Math.floor(min + random * (max - min + 1));
}

function getTodaysSeed() {
  const today = new Date();
  return today.getFullYear() * 10000 + (today.getMonth() + 1) * 100 + today.getDate();
}

// 사용
const min = 0; 
const max17 = years17 - 1;
const max18 = years18 - 1;
const max19 = years19 - 1;
const seed = getTodaysSeed(); // 오늘의 날짜를 시드로 변환
const randomNumber17 = seededRandom(seed, min, max17);
const randomNumber18 = seededRandom(seed, min, max18);
const randomNumber19 = seededRandom(seed, min, max19);
const ulElement = document.getElementById('ul');
ulElement.innerHTML = '';

// "오늘의 추천곡" 제목을 추가
const titleDiv = document.createElement('div');
titleDiv.textContent = "오늘의 추천곡";
ulElement.appendChild(titleDiv);

// 각 연도별 추천곡과 링크를 추가
const songlists = [songlists17, songlists18, songlists19];
const links = [links17, links18, links19];
const randomNumbers = [randomNumber17, randomNumber18, randomNumber19];

songlists.forEach((songlist, index) => {
  const song = songlist[randomNumbers[index]];
  const link = links[index][randomNumbers[index]];

  // 새로운 div 요소 생성
  const songDiv = document.createElement('div');
  
  // 하이퍼링크(a) 요소 생성 및 설정
  const songLink = document.createElement('a');
  songLink.href = link; // 링크 설정
  songLink.textContent = song; // 텍스트 내용 설정
  songLink.target = "_blank"; // 링크를 새 탭에서 열도록 설정

  // 하이퍼링크를 div에 추가하고, 이 div를 ul 요소의 자식으로 추가
  songDiv.appendChild(songLink);
  ulElement.appendChild(songDiv);
});
//오늘의 추천곡 끝