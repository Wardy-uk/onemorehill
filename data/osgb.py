"""OSGB36 easting/northing -> WGS84 lat/lon (Airy 1830 + Helmert). ~few m accuracy."""
import math
def en_to_wgs84(E,N):
    a,b=6377563.396,6356256.909           # Airy 1830
    F0,lat0,lon0=0.9996012717,math.radians(49),math.radians(-2)
    N0,E0=-100000.0,400000.0
    e2=1-(b*b)/(a*a); n=(a-b)/(a+b)
    lat=lat0; M=0
    while abs(N-N0-M)>=0.00001:
        lat=(N-N0-M)/(a*F0)+lat
        Ma=(1+n+1.25*n*n+1.25*n**3)*(lat-lat0)
        Mb=(3*n+3*n*n+2.625*n**3)*math.sin(lat-lat0)*math.cos(lat+lat0)
        Mc=(1.875*n*n+1.875*n**3)*math.sin(2*(lat-lat0))*math.cos(2*(lat+lat0))
        Md=(35/24)*n**3*math.sin(3*(lat-lat0))*math.cos(3*(lat+lat0))
        M=b*F0*(Ma-Mb+Mc-Md)
    sl=math.sin(lat); cl=math.cos(lat); tl=math.tan(lat)
    nu=a*F0/math.sqrt(1-e2*sl*sl); rho=a*F0*(1-e2)/((1-e2*sl*sl)**1.5); eta2=nu/rho-1
    VII=tl/(2*rho*nu)
    VIII=tl/(24*rho*nu**3)*(5+3*tl*tl+eta2-9*tl*tl*eta2)
    IX=tl/(720*rho*nu**5)*(61+90*tl*tl+45*tl**4)
    X=1/(cl*nu); XI=1/(cl*6*nu**3)*(nu/rho+2*tl*tl)
    XII=1/(cl*120*nu**5)*(5+28*tl*tl+24*tl**4)
    XIIA=1/(cl*5040*nu**7)*(61+662*tl*tl+1320*tl**4+720*tl**6)
    dE=E-E0
    latA=lat-VII*dE**2+VIII*dE**4-IX*dE**6
    lonA=lon0+X*dE-XI*dE**3+XII*dE**5-XIIA*dE**7
    # Helmert OSGB36 -> WGS84
    H=24.7; x1=(nu/F0+H)*math.cos(latA)*math.cos(lonA)
    y1=(nu/F0+H)*math.cos(latA)*math.sin(lonA)
    z1=((1-e2)*nu/F0+H)*math.sin(latA)
    tx,ty,tz=446.448,-125.157,542.060
    rx,ry,rz=[math.radians(v/3600) for v in (0.1502,0.2470,0.8421)]
    s=-20.4894e-6
    x2=tx+(1+s)*x1-rz*y1+ry*z1
    y2=ty+rz*x1+(1+s)*y1-rx*z1
    z2=tz-ry*x1+rx*y1+(1+s)*z1
    a2,b2=6378137.0,6356752.3142
    e22=1-(b2*b2)/(a2*a2); p=math.sqrt(x2*x2+y2*y2)
    la=math.atan2(z2,p*(1-e22)); lap=2*math.pi
    while abs(la-lap)>1e-12:
        v=a2/math.sqrt(1-e22*math.sin(la)**2); lap=la
        la=math.atan2(z2+e22*v*math.sin(la),p)
    return math.degrees(la), math.degrees(math.atan2(y2,x2))
