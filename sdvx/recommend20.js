var songlists20 = [
  "Λkasha (20)",
  "APØCALYPSE RAY (20)",
  "Bl∞min' (20)",
  "HeaveИ's Rain (20)",
  "MixxioN (20)",
  "《Re:miniscence》 (20)",
  "SuddeИDeath (20)",
  "XHRONOXAPSULΞ (20)",
  "You Are My Best RivaL!! (20)",
  "いまきみに (20)",
  "666 (20)",
  "ΣgØ (20)",
  "* Erm, could it be a Spatiotemporal　ShockWAVE Syndrome...? (20)",
  "MAYHEM (20)",
  "VVelcome!! (20)",
  "ΣmbryØ (20)",
  "*Feels Seasickness...* (20)",
  "FIN4LE ～終止線の彼方へ～ (20)",
  "HE4VEN ～天国へようこそ～ (20)",
  "I (20)",
  "iLLness LiLin (20)",
  "WHITEOUT (20)",
  "Xronièr (20)",
  "Lachryma《Re:Queen'M》 (20)"
];

xi = songlists20.length; // 곡 갯수
xxi.innerHTML = "전체 곡 "+ xi +"곡";

function input() {
  $("ul").empty();
  var howmany = document.getElementById("select1").value;
    for(i=0;i<howmany;i++){
      var newDiv = document.createElement('div');
      newDiv.id = "result"+i
      var newContent = document.createTextNode(songlists20[Math.floor(Math.random()*(xi-1))]);
      newDiv.appendChild(newContent);
      document.getElementById("ul").appendChild(newDiv);
    }
  message2.innerHTML = "마음에 들지 않는다면 재추첨 버튼을 눌러주세요"
  cc.innerHTML = "재추첨"

};
