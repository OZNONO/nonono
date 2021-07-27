jQuery(".nav-link").hover( function () { jQuery(this).addClass("active"); }, function () { jQuery(this).removeClass("active"); } );
function loadran() {
 $("#bonmoon").empty();
 bonmoon.innerHTML = "<p>곡 선택장애가 왔거나 마지막 코인 고렙하고싶을때 등등 눌러주세욤</p>\
 <a href=\"./recommend20.html\" class=\"btn btn-default border\">20레벨 무작위 곡 추천</a><br><br>\
 <a href=\"./recommend19.html\" class=\"btn btn-secondary border\">19레벨 무작위 곡 추천</a><br><br>\
 <a href=\"./recommend18.html\" class=\"btn btn-default border\">18레벨 무작위 곡 추천</a><br><br>\
 <a href=\"./recommend17.html\" class=\"btn btn-secondary border\">17레벨 무작위 곡 추천</a><br><br>\
 <hr>\
 <a href=\"./recommend1819.html\" class=\"btn btn-default border\">18~19레벨 무작위 곡 추천</a><br><br>\
 <a href=\"./recommend1718.html\" class=\"btn btn-secondary border\">17~18레벨 무작위 곡 추천</a><br><br>";
};


function loadrec() {
   $("#bonmoon").empty();
   bonmoon.innerHTML = "<p> 직접 고른 추천곡들을 모았습니다.</p>\
     <a href=\"./rec18.html\" class=\"btn btn-default border\">엄선된 18레벨 곡 추천</a><br><br>\
     <a href=\"./rec17.html\" class=\"btn btn-secondary border\">엄선된 17레벨 곡 추천</a><br><br>\
     <a href=\"#\" class=\"btn btn-default border\">발광(폐쇄됨)</a><br><br></p>\
     <hr>"

};

function loadmemo() {
   $("#bonmoon").empty();
   bonmoon.innerHTML = "<p>20200502 탭 생성</p><hr>\
   <p>20200509 발광 문서 추가. 고렙 위주로.</p><hr>\
   <p>닫음. 퍼얼허싈?</p><hr>\
   <p><a href=\"./PUCed18.html\" class=\"btn btn-default border\">18PUC기록</a><br><br></p>"
}
