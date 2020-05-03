jQuery(".nav-link").hover( function () { jQuery(this).addClass("active"); }, function () { jQuery(this).removeClass("active"); } );
function loadsogae() {
 $("#bonmoon").empty();
 bonmoon.innerHTML = "<p>軍人 2019.05.27~2020.12.25</p>\
 <p>Contact : open.kakao.com/me/OZNONO</p>\
 <p>twitter : @ji112</p>\
 <p>개인 웹사이트 입니다. 모 동네의 블러드캣에서 영감을 받았대요.</p>\
 <p><button class=\"btn btn-default border\" onclick=\"location.href='http://oznono.com/sdvx';\">SDVX</button></p>";
};


function loadoz() {
   $("#bonmoon").empty();
   bonmoon.innerHTML = "<p>since 2018.08.05~</p>\
   				<p>팀장을 맡고 있습니다. 군인이 늘어나고 있습니다.</p>\
   				<p>문의사항은 연락 주세요.</p>"
};

function loadmemo() {
   $("#bonmoon").empty();
   bonmoon.innerHTML = "<p>메모입니다.</p>"
}
