#pragma once

/*
MAPPY
    signtype
    111 오른쪽 급커브
    112 왼쪽 급커브
    113 굽은도로
    118, 127 어린이보호구역
    122 : 좁아지는 도로
    124 : 과속방지턱
    129 : 주정차
    131 : 단속카메라(신호위반카메라)  
    135 : 고정식(버스단속구간)  - 호야
    150 : 경찰차(이동식단속구간)  - 호야
    165 : 구간단속   
    197 : 구간단속 
    198 차선변경금지시작
    199 차선변경금지종료
    129 주정차금지구간
    123 철길건널목
    200 : 단속구간(고정형 이동식)
    231 : 단속(카메라, 신호위반)    - 어린이.
    246 버스전용차로단속
    247 과적단속
    248 교통정보수집
    249 추월금지구간
    250 갓길단속
    251 적재불량단속
*/


typedef enum TrafficSign {
  TS_CURVE_RIGHT = 111,  // 오른쪽 급커브
  TS_CURVE_LEFT = 112,   // 왼쪽 급커브
  TS_BEND_ROAD = 113,    // 굽은도로
  TS_SCHOOL_ZONE1 = 118,  // 어린이보호구역
  TS_SCHOOL_ZONE2 = 127,  // 어린이보호구역
  TS_NARROW_ROAD = 122,   // 좁아지는 도로
  TS_RAIL_ROAD = 123,     // 철길건널목
  TS_BUMP_ROAD =  124,  // 과속방지턱
  TS_PARK_CRACKDOWN  = 129,  // 주정차단속
  TS_CAMERA1  = 131,  // 단속카메라(신호위반카메라)  
  TS_CAMERA2_BUS  = 135,  // 고정식  - 호야
  TS_CAMERA3  = 150,  // 경찰차(이동식)  - 호야
  TS_INTERVAL  = 165,  // 구간 단속
  TS_VARIABLE  = 195,  // 가변구간
  TS_INTERVAL2  = 197,  // 구간 단속2
  TS_LANE_CHANGE1  = 198,  // 차선변경금지시작
  TS_ANE_CHANGE2  = 199,  // 차선변경금지종료
  TS_CAMERA4  = 200,  // 단속구간(고정형 이동식)
  TS_CAMERA5  = 231,  // 단속(카메라, 신호위반)    
  TS_BUS_ONLY  = 246,  // 버스전용차로단속
  TS_LOAD_OVER  = 247,  // 과적단속
  TS_TRAFFIC_INFO  = 248,  // 교통정보수집
  TS_OVERTRAK  = 249,  // 추월금지구간
  TS_SHOULDER  = 250,  // 갓길단속
  TS_LOAD_POOR  = 251,  // 적재불량단속  
} TrafficSign;


// TMAP
   //  opkrspdlimit,opkrspd2limit
   //  opkrspddist,opkrspd2dist
   //  opkrsigntype,opkrspdsign
/*
   opkrsigntype  값정리
    1 과속 단속 카메라
    2. 구간단속 시작
    3  구간단속 종료
    4. 구간간속 진향중
    7. 이동식 카메라
    8. Box형 카메라
    13.
    29. 사고다발  x
    30. 급커브     x
    46.
    63  졸움쉼터  x
*/

 // 1. 안심모드
    // - opkrspd2dist, opkrspdsign, opkrspdlimit,

//  2. overlay mode
    // - opkrspd2limit, opkrsigntype, opkrspddist


/* iNavi Road signtype
 101 이어지는 커브 
101 연속 커브
 102 추돌주의 
107 과속방지턱 
5 이동식 
105 낙석주의
 15 고정식 
10 합류
 9 과적단속 
111 철길건널목 
18 이벤트 발생
 203 녹색교통 

iNavi Cam signtype 
11, 12 구간단속 
6 이동식단속 
2 고정식단속 
2 신호및속도단속 
1 안전속도 
3 신호위반단속 
4, 7 버스전용차로 단속 
5 교통량 측정
 8 주차위반 단속 
101 이어지는 커브 
101 연속 커브 
15 박스형카메라 
16 스쿨존 
18 실버존 
118 야생동몰 
20 차선변경금지 
203 녹색교통 
204 미끄럼주의 

mappy signtype 
111 오른쪽 급커브 
112 왼쪽 급커브
 113 굽은도로 
118, 127 어린이보호구역 
122 좁아지는 도로 
124 과속방지턱 
129 주정차 
131 단속카메라(신호위반카메라) 
135 고정식(버스단속구간) - 호야
 150 경찰차(이동식단속구간) - 호야 
165 구간단속 
195, 197 구간단속, 가변속도제한구간 
198 차선변경금지시작

typedef enum TrafficSign_TMAP {
  TM_CAMERA1  = 1,  // 단속카메라(신호위반카메라)  
  TM_INTERVAL  = 2,  // 구간단속 시작
  TM_INTERVAL2  = 3,  // 구간단속 종료
  TM_INTERVAL4  = 4,  // 구간간속 진향중
  TM_CAMERA3  = 7,  // 7. 이동식 카메라
  TM_CAMERA4  = 8,  // 8. Box형 카메라

} TrafficSign_TMAP;
