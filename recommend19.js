        var songlists19 = [
        "9TH5IN [ MXM 19 ]",
        "ANGER of the GOD [ MXM 19 ]",
        "ENDYMION [ MXM 19 ]",
        "Ghost Family Living In Grabeyard [ MXM 19 ]",
        "Lancelot ～Flame of the Rebellion～ [ MXM 19 ]",
        "OUTERHEΛVEN [ MXM 19 ]",
        "ЯeviveR [ MXM 19 ]",
        "TENKAICHI ULTIMATE BOSSRUSH MEDLEY [ MXM 19 ]",
        "THE凸GENERATOR [ MXM 19 ]",
        "Trill auf G [ MXM 19 ]",
        "voltississimo [ MXM 19 ]",
        "θコトノハθカプセルθ [ MXM 19 ]",
        "色を喪った街 [ MXM 19 ]",
        "A Lasting Promise [ MXM 19 ]",
        "Absolute Domination [ MXM 19 ]",
        "Awakening [ MXM 19 ]",
        "BELOBOG [ MXM 19 ]",
        "Chrono Diver -PENDULUMs- [ MXM 19 ]",
        "Cross Fire [ MXM 19 ]",
        "Deadly force [ MXM 19 ]",
        "Dyscontrolled Galaxy [ MXM 19 ]",
        "Elemental Creation [ MXM 19 ]",
        "Failnaught [ MXM 19 ]",
        "Fin.ArcDeaR [ MXM 19 ]",
        "Fly Like You [ MXM 19 ]",
        "FREEDOM DiVE [ MXM 19 ]",
        "GERBERA -For Finalists- [ MXM 19 ]",
        "GODHEART [ MXM 19 ]",
        "Immortal saga [ MXM 19 ]",
        "KAC 2013 ULTIMATE MEDLEY -HISTORIA SOUND VOLTEX- Empress Side [ MXM 19 ]",
        "Last Resort [ MXM 19 ]",
        "Sailing Force [ MXM 19 ]",
        "Staring at star [ MXM 19 ]",
        "TWO-TORIAL [ MXM 19 ]",
        "Xeroa [ MXM 19 ]",
        "セイレーン ～悲壮の竪琴～ [ MXM 19 ]",
        "逆月 [ MXM 19 ]",
        "FLOWER [ HVN 19 ]",
        "Got more raves？ [ HVN 19 ]",
        "きたさいたま2000 [ HVN 19 ]",
        "極圏 [ HVN 19 ]",
        "ΑΩ [ GRV 19 ]",
        "Blastix Riotz [ GRV 19 ]",
        "DIABLOSIS::Nāga [ GRV 19 ]",
        "Everlasting Message [ GRV 19 ]",
        "FLügeL《Λrp:ΣggyØ》 [ GRV 19 ]",
        "KAC 2013 ULTIMATE MEDLEY -HISTORIA SOUND VOLTEX- Emperor Side [ GRV 19 ]",
        "Load=Crossight [ GRV 19 ]",
        "Preserved Valkyria [ GRV 19 ]",
        "XyHATTE [ GRV 19 ]",
        "月光乱舞 [ GRV 19 ]",
        "Innocent Tempest[ VVD 19 ]",
        "ラクガキスト [ VVD 19 ]",
        "音楽 -resolve-[ VVD 19 ]",
        "Booths of Fighters [ HVN 19 ]",
        "For UltraPlayers [ HVN 19 ]",
        "INSECTICIDE [ HVN 19 ]",
        "Quietus Ray [ HVN 19 ]",
        "Verse IV [ HVN 19 ]",
        "バンブーソード・ガール [ HVN 19 ]",
        "Bangin' Burst [ GRV 19 ]",
        "Black Emperor [ GRV 19 ]",
        "BLACK or WHITE? [ GRV 19 ]",
        "Growth Memories [ GRV 19 ]",
        "snow storm -euphoria- [ GRV 19 ]",
        "XROSS INFECTION [ GRV 19 ]",
        "大宇宙ステージ [ GRV 19 ]",
        "Ganymede kamome mix [ INF 19 ]"
      ];

      xi = songlists19.length; // 곡 갯수
      xxi.innerHTML = "전체 곡 "+ xi +"곡";

      function input() {
        $("ul").empty();
        var howmany = document.getElementById("select1").value;
          for(i=0;i<howmany;i++){
            var newDiv = document.createElement('div');
            newDiv.id = "result"+i
            var newContent = document.createTextNode(songlists19[Math.floor(Math.random()*(xi-1))]);
            newDiv.appendChild(newContent);
            document.getElementById("ul").appendChild(newDiv);
          }
        message2.innerHTML = "마음에 들지 않는다면 재추첨 버튼을 눌러주세요"
        cc.innerHTML = "재추첨"

      };
