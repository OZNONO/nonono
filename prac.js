var songlists19 = {
"0":"9TH5IN",
"1":"ANGER of the GOD",
"2":"ENDYMION",
"3":"Ghost Family Living In Grabeyard",
"4":"Lancelot ～Flame of the Rebellion～",
"5":"OUTERHEΛVEN",
"6":"ЯeviveR",
"7":"TENKAICHI ULTIMATE BOSSRUSH MEDLEY",
"8":"THE凸GENERATOR",
"9":"Trill auf G",
"10":"voltississimo",
"11":"θコトノハθカプセルθ",
"12":"色を喪った街",
"13":"A Lasting Promise",
"14":"Absolute Domination",
"15":"Awakening",
"16":"BELOBOG",
"17":"Chrono Diver -PENDULUMs-",
"18":"Cross Fire",
"19":"Deadly force",
"20":"Dyscontrolled Galaxy",
"21":"Elemental Creation",
"22":"Failnaught",
"23":"Fin.ArcDeaR",
"24":"Fly Like You",
"25":"FREEDOM DiVE",
"26":"GERBERA -For Finalists-",
"27":"GODHEART",
"28":"Immortal saga",
"29":"KAC 2013 ULTIMATE MEDLEY -HISTORIA SOUND VOLTEX- Empress Side",
"30":"Last Resort",
"31":"Sailing Force",
"32":"Staring at star",
"33":"TWO-TORIAL",
"34":"Xeroa",
"35":"セイレーン ～悲壮の竪琴～",
"36":"逆月",
"37":"FLOWER",
"38":"Got more raves？",
"39":"きたさいたま2000",
"40":"極圏",
"41":"ΑΩ",
"42":"Blastix Riotz",
"43":"DIABLOSIS::Nāga",
"44":"Everlasting Message",
"45":"FLügeL《Λrp:ΣggyØ》",
"46":"KAC 2013 ULTIMATE MEDLEY -HISTORIA SOUND VOLTEX- Emperor Side",
"47":"Load=Crossight",
"48":"Preserved Valkyria",
"49":"XyHATTE",
"50":"月光乱舞",
"51":"Innocent Tempest",
"52":"ラクガキスト",
"53":"音楽 -resolve-",
"54":"Booths of Fighters",
"55":"For UltraPlayers",
"56":"INSECTICIDE",
"57":"Quietus Ray",
"58":"Verse IV",
"59":"バンブーソード・ガール",
"60":"Bangin' Burst",
"61":"Black Emperor",
"62":"BLACK or WHITE?",
"63":"Growth Memories",
"64":"snow storm -euphoria-",
"65":"XROSS INFECTION",
"66":"大宇宙ステージ",
"67":"Ganymede kamome mix"
};

function input(){
  $("ul").empty();
  var howmany = document.getElementById("select1").value;
    for(i=0;i<howmany;i++){
      var newDiv = document.createElement('div');
      newDiv.id = "result"+i
      var newContent = document.createTextNode(songlists19[Math.floor(Math.random()*67)]);
      newDiv.appendChild(newContent);
      document.getElementById("ul").appendChild(newDiv);
    }
  message2.innerHTML = "마음에 들지 않는다면 재추첨 버튼을 눌러주세요"
  cc.innerHTML = "재추첨"

}

function output(){
document.write()
}
