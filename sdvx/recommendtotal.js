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