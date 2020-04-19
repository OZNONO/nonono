var songlists20 = [

"666 [MXM 20]",
"ΣgØ [MXM 20]",
"* Erm, could it be a Spatiotemporal ShockWAVE Syndrome...? [MXM 20]",
"ΣmbryØ [MXM 20]",
"Feels Seasickness...* [MXM 20]",
"FIN4LE ～終止線の彼方へ～ [MXM 20]",
"HE4VEN ～天国へようこそ～ [MXM 20]",
"I [MXM 20]",
"iLLness LiLin [MXM 20]",
"WHITEOUT [MXM 20]",
"Xronièr [MXM 20]",
"Lachryma《Re:Queen'M》 [GRV 20]",

]

function input(){
  $("ul").empty();
  var howmany = document.getElementById("input").value;
    for(i=0;i<howmany;i++){
      var newDiv = document.createElement('div');
      newDiv.id = "result"+i
      var newContent = document.createTextNode(songlists20[Math.floor(Math.random()*12)]);
      newDiv.appendChild(newContent);
      document.getElementById("ul").appendChild(newDiv);
    }
  message2.innerHTML = "마음에 들지 않는다면 재추첨 버튼을 눌러주세요"
  cc.innerHTML = "재추첨"

}

function output(){
document.write()
}
