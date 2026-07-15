function Tr=T_delay(E,rou0)
    pi=3.1415926535;
    pos=[113.91168121,22.52138978,23.36];
    lat=pos(2)*pi/180;
    h=pos(3);
    %大气压
    p=1013.25*(1-2.2557e-5*h)^5.2568;
    %大气绝对温度
    T=15.0-6.5e-3*h+273.15;
    %水汽压e
    hrel=0.7;
    e=6.108*exp((17.15*T-4684.0)/(T-38.45))*hrel;
    %干湿分量
    z=(90-E)*pi/180;
    Tdry=0.0022768*p/(1.0-0.00266*cos(2*lat)-0.00028e-3*h)/cos(z);
    Twet=0.0022768*(1255/T+0.05)*e/cos(z);
    %对流层延迟
    T_trop=Tdry+Twet;
    %改正后伪距
    rou=rou0+T_trop;
    
    Tr=[T_trop,rou];
    disp(sprintf('对流层延迟为%f，修正后的伪距为%.4f',T_trop,rou));
    