
function Ir=I_delay(type,E,A,rou0,t_gps)
    %%
    %Klobuchar模型计算电离层延迟
    pi=3.1415926535;
%     type=input('输入卫星类型，如''gps''或''bds'':')
%     pos=input('输入接收机位置，如,[113.91168121,22.52138978,23.36]:');
%     rou0=input('输入改正前伪距，如,21457996.543:')
    % %测试
    %i=[1.2107e-08,-7.4506e-09,-1.1921e-07,5.9605e-08,9.8304e+04,-8.1920e+04,-1.9661e+05,4.5875e+05];
    %北斗8参数
    i=[1.5832e-08,1.4901e-08,-4.7684e-07,8.9407e-07,1.2288e+05,4.9152e+04,-1.8350e+06,2.2282e+06];
    pos=[113.91168121,22.52138978,23.36];

    %仰角
%     E=input('输入仰角(°)，如,57.76:');
    E=E/180; %转换为弧度
    %方位角
%     A=input('输入方位角(°)，如,79.28:');
    A=A/180;%转换为弧度
    %天内秒
%     t_gps=input('输入GPS天内秒，如,30:');

    %电离层8个参数
    a0=i(1);a1=i(2);a2=i(3);a3=i(4);
    b0=i(5);b1=i(6);b2=i(7);b3=i(8);
    %接收机位置
    lat_u=pos(2)/180; lon_u=pos(1)/180; %转化为弧度
    gusai=0.0137/(E+0.11)-0.022;
    %地理纬度
    lat_i=lat_u+gusai*cos(A*pi);
    if abs(lat_i)<=0.416
        lat_i=lat_i;
    elseif lat_i>0.416
        lat_i=0.416;
    else
        lat_i=-0.416;
    end
    %地理经度
    lon_i=lon_u+(gusai*sin(A*pi))/cos(lat_i*pi);
    %%
    t=43200*lon_i+t_gps;%t在[0,86400]内

    F=1.0+16.0*(0.53-E)^3;
    %%
    if type=='gps'
        %地磁纬度
        lat_m=lat_i+0.064*cos((lon_i-1.617)*pi);
        %gps的AMP和PER
        AMP=a0+a1*lat_m+a2*lat_m^2+a3*lat_m^3;
        if AMP>=0
            AMP=AMP;
        elseif AMP==0
            AMP=0;
        else
            disp('AMP计算错误');
        end
        PER=(b0+(b1+(b2+b3*lat_m)*lat_m)*lat_m);
        if PER>=72000
            PER=PER;
        elseif PER<72000
            PER=72000;
        else
            disp('PER计算错误');
        end
        %gps电离层延迟
        x=(2*pi*(t-50400.0))/PER;
        if abs(x)<pi/2
            I=F*(5e-9+AMP*(1.0-x^2/2+x^4/24));
        else
            I=F*5e-9;
        end

    end %if type=='gps'
    %%
    if type=='bds'
     %%   
        %lat_i=lat_i+0.064*cos((lon_i-1.617)*pi);%地磁纬度
        %bds的AMP和PER
        AMP=(a0+(a1+(a2+a3*lat_i)*lat_i)*lat_i);
        if AMP>=0
            AMP=AMP;
        elseif AMP==0
            AMP=0;
        else
            disp('AMP计算错误');
        end
        PER=(b0+(b1+(b2+b3*lat_i)*lat_i)*lat_i);
        if PER>=72000
            PER=PER;
        elseif PER<72000
            PER=72000;
        else
            disp('PER计算错误');
        end
        %bds电离层延迟
        x=(2*pi*(t-50400))/PER;
        if abs(x)<pi/2
            I=F*(5e-9+AMP*(1.0-x^2/2+x^4/24));
        else
            I=F*5e-9;
        end
        %北斗电离层延迟修正
        f_gps=1575.42; f_bds=1561.098; %MHz
        I=(f_gps^2/f_bds^2)*I;

    end %if type=='bds'

    %路径延迟
        %I=I*2.99792458e8;
        I=I*3e8;
        rou=rou0+I;
        Ir=[I,rou];
        %输出
        disp(sprintf('位于北纬%f°，东经%f°的%s接收机:',pos(1),pos(2),type));
        disp(sprintf('电离层延迟为%f,修正后的伪距为%.4f',I,rou));
        
end
    