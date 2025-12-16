#!/usr/bin/env python3
# requires-python = ">=3.6"
# -*- coding: utf-8 -*-
import argparse
import os
import re
import shutil
import stat
import time
from collections import defaultdict, namedtuple

try:
	import multiCMD  # type: ignore
	assert float(multiCMD.version) >= 1.41
except Exception:
	import sys,types,base64,lzma  # noqa: E401
	multiCMD = types.ModuleType("multiCMD")
	sys.modules["multiCMD"] = multiCMD
	_SRC_B85=b'rAT%)=o\\O*k16n/!WXAE)uos=&C4J&i\'[,QV-O\'XRn@>\';ET$AFlGh.R(o"q(b5T&o>3f]hV74Y3u>"H]--h>bSUZui+lBXf\\sVB/2;6s>`+nN4oSnOJY\\%m;g^q_+3mWal)O^WeXIN-LSGHX/nW[I3)i\\28j(jX1o_SC16_H+pH*-._3;NL0?7Dtjf$jS#3<K(W=5RSrPN_O-HNd<[\'hJI`eMWdZM9l;_)6+Qg6Y6?lSG>+oo$[/V-HbF1CW,ug<f%bH305F%ckk1XcYG\'_LXr3I_Y"nVc\\3SU?.6CO4:s:X0U@#RSL(DZ]N&;S=a6rbn;PX)_%M]ou=ir4$]KN6dt9i],]VF"^.]9@QU(i[d:J=eaDM-JoOR7SVGs9&W]@XWJ8F#=_DOR:iA6_r(ec.H2D6F6B1s!d)NFYF0-M<&e1qAWreY]#[nl$HE$kc23Q^9RQHqjdmP..#an8%Qe*GImT_dhAI_e/&658j9bLBoL/V@Ar%(CK$\'mX5%Uq/[fnpS`ESDa9iYcl]Fd\'uD\\&@:)U@ju*UE5S+/oXf&[\\h]r:c.B3$]d$c-Xn(5GM,)?Ae9I?Z#[eiUI(Tn+0MYqj]2"GGa/"+bu@W#gA,Fi,KLtk)Z4E-i$"G44\'6SfS:c6t&%;;T1,CR0H,mfkn^dT/]F.KN2ZIcUJ/WQ*&nD]0lN<o`dJ[>B3$tB/V9Ua="=V[E@04Z-#oSa3LE`O:-<G^]jZ\\1N5@[tLi!2j_IJuu([OjbUHoVn_eUcPX="4K>W->PZl"Ijg\\s`/tXiVE#]rRG:[RJSb\'/@KV6o.M;>7FBHgo&JX&]bidY_5dpgiW8\'^?b<p^?#mB.BqAq(X^V8eKt#tMVQnbr%)8geKiF8=!PE[%0WX\'32$HoqsAa+B6+ujqN7gPY1%X-lommRIt<1!EJ#0?\'U\'S]L1QN\\&?5DgC16[%Zh+j,3\'c-m9,"D*ipj7AeG\'Ham&;XA=O;"UDJj_Q<CjkJ5Em1:RJ^99A%;Yh0ajgQ6d>m^fEekC/-1kLES.X.6.<*$nLRJ,+&7/P4p[L7Q\'Q1A4r?gW+0"a]FHi6o>AWG]b)Q%VZ(e>O"o#-q$2XZ(?=G9u!)ulbRo.8d)"`+9Gg\\X<o;h2lQ`_^0V-\\oZXNhc=T#mNaJdf*I!OBu!2Bgpolj6k=kBo8Gi:2\'9!\\$<inY^"/N]XJYD$A:<A&2qO2r(;tZ<KoM67Gbfp\\lb(DX=/N0<5%"mNa;fL!E6gZcL$ad5QBYUcu8TTdO9+_S8#$50PScDog&Ldff/Z/Eab#<-gn&A+U<tq@-ok+DC>Sp="[R\\.em5U(NjVJ7a@-ZV]pV+JXunQgH^-(=e\'$aTFlXLr#$p63Qc(GCuD*>/ZW\'+/q\\eDI)9;`S##RY%=?ndDC,cLdZ2CnK"<uc9u[M_,;EVks;%h"//G=_ZpFc6_m:\\k86Vg,[Pe&%<MZo*M<T[R7<5IfG3l[adjbqLVCm*O>^CHSTNC$a3\\!cIm9N0*>dWK>BMh>bfi5(ec"XTD$[JmCLQT*L-<ZY@c0fR#9b;f@E(\')fM4JO^s38$dMpgY_H?JmW#/Ze^/5(@g2+a+*^*^r+CT%Y?nl^SB!&HoP)eSYI-F"H3lNgm_VW0tkcL-XANb^Q-!AHhI4:ZG1WtR@).\\rQWu<qKK,<K_*c`a,k/U9PRMZnM!aU/*WHA:[V\'NnJ[@ta@ms!Atel@rt>>bl8:Sktt5aDT#Ii8\'t\'NMJ/P>q<If@bT]>[EPc41?hQDm,%ho3*t+PJ].CKEa#`RqfDF*6X=G)?NYgo*rA`NL5I[9.2B6@=p:\\r0TbI$pF>n*\\67%a.R@8*oUT)ErlnF<j.V[F"cX"?V;($#b+_Xm#)E&J\\U\'p:TClH(;lQ^)`u7Q,8(NI`NLf=l1=)C`;ehWIVAl2oBFL6EbY6VR`*3Un*h^[?i<Y\'k-l*nOdDAM@^HAsReYjo]F#A&s.<$.Oq;UZp\'n-Depd*qA,465bu?<AfT>i;Z@a\\5lGK)V:,OODng.%ZN:0da,.P;pT<%>AU^X!RMfQl)T9B!#-eB7ln=%i[rOC;G5FpkM<YAfMeX*N>Dn4HoL3\\Z9["=0jc\\Y@_@"\'#P@+!PcL32GDG<%\'&[C.7TE*+L<:!1YRQsJ?([u]pFat`quk9dd#d$q_,ku?.EekQu+m9[J`fN4W:Y_NM<O[Ra%e:`bW3iVS&cAKV"s#NA(lk2UQjh`4W8RT>V9Yk2Yo+09EZj"R%r<Ib2qj+LOnUBSa07#F!NWIGW*G^KeAUJ.M<7k$;DH<87C6qug[TCC*9HraO2m;d5]Mbbu_8Mk99P"NkQDp35$Hr9QrfcW-f2hYC@Rcmen92f.3on5a6,;?A)lVU^J?GQIKdQb;_Q*?%St*ptKCllgKBm)qB3i0ZNAdJHJ6@bET=h28B=Lk>+g$()\'j0?V/PRHaA/sVLK6sP\';p"4m[89`ILR8irFN#,/#&%`&$D\\-5Nq<SUNrjr\'Cc$ITXNHMtqsU2F`;M@[5P1u%"2i/bp,gK1C&CXc\\2nqP?D-Z*6[s]SE6AfLBXTJcp2+"TnLq1XoqEK^b:;MnFNSfdHO`Y$*;-eD^a;@\'26`,O93Nr#(oe[`##UFdg33!MUR`L+^2%=P:75o26e6V0]!1$rqW`s\\s%hC&kd&e@ee*)rK6pX[:\\a4Ri?:RUk)Z@OGk-%^k2!*f"i\'i<RHH85%j7q+*<7];XOY9u;GmTQq=]ob.sAIG@9E2HYpPdlZI/*\\)C]SN71"[>@\',;;\':`G1Xof(=9b).3QP9+_iK3V=KB$4fQs3R7ndt5SASrC?g@C.@[<A2p#]_cg"]g\\g3\\$JC_ih"<j7eaoK]&p<^Dehj57+C%n1U9ZgU[,/<gA_\\lr3FR2VhsiA_`))m`-+4H1_ca+++E2r/68I[.)A\\pU.?VW.Lkj:o%FuA4Akas,OjX(X\\]U?#cE\'cPc.KND9KRg2fSFPdrU>M"\\#L8]`XD[r3nG)&AWR);gV!Rh(DV+J[0*"%[7_d&";n-[&WsFAnqn^jS5QHZ]J.eX<NfblS995&\\E%>3TJXR0JJ>i.nVdpDic@[(EY+?O%giHL9P:n"9h9,2TNP]Jtp)Ha<e5f(t&9U\\W)IPToWun8N\'YpF$pp\\8l\'MIf6]"/l@A>\\LSPAdPd)h_u#Q8dntc$C<MoBaj]d6]`6.s+%c4r>DL<P*(F=hY(nc\\,H[aCj&J9\'h%\\q6-C7Xe[r>-@Tof6qh*m.,U;s:u*8j!3nUo\'5)<"J;)_Z8U=n$Q\'A(I\\mIhYrCf;9>b":8jQ#ecJ_7;u=mmJ$J-gQSs97/@a=Q>^-,ZQ]s=_ti7JM(2DWKrRpEWQ.02HIm[25!b-(0Zc>?*fS7qaf[iXJ=fUW!0!C?3p5"_A-U^uZbIg&(-slh8\'?-GrFkmiK=0cj@FBC=UCaGr\\\\TH]IFK!PSQ"XT9WlD%P38VA^<B);"_QdsM7mG;bg>X$\'kh02[AuB2lX^_"B$jS7Xd9:2+sX,._mK&["BC0Kg)4MB574OODXi#r.1D>9Qm+NQfl+I=P3Z@#QkU2rnnJsTNM:GKr3>9A4BkjXh884k0&9A4+p*Z;C)Ko%cDBi1$!!F"#WB%0LnKO1oZ3k$-o$Eo$r%6?KdDu9&1F%r?Na0Om<,*Ur12k;lBaY96.K/!$AA6mHeLTY7?;0.<=Xhk*n$NkB8QeZLKE%q)kA\\_g7qK&S$i9u][i]f_H%kIQLP\\?OV3fM4D*BD2a_bC4*Ch;NsL;MUsDqj"@&VLio5?2elO+W`Ql)?@`A(c#^o)A[@l*WKiRip@X=,#i3=37EUT^65%n.!44b>UQJcsNVL-1eFiu4;q_S[h$@5,*TRWXYn<h=+PCJ*Ye/:9$[0I;d_ugZ.&MBund7BI-:/RlDg<D1C\\uQ-ADI[g9Lg7u2i@%:L\\DDKu&CGXqV%Rd&qFMg)XKLtU:9U0XLr0T;+WEWQq=8n[D7?qL+0/dtVg8iFreY)?0aYj*[)O2ODHP\\`=YEX_(=+\'Ub0<q2SM&a^B#^p5=S340Vo:7frfXo^[_u_aJ!_eH#@1S_E89R&5agGrY8/&sK8GJV?+362\\ZQ#;-X*a>33Q165A4lc7FpO%G:u$g@A_XX&[*\'8+V*l^\\.[k)A7bj^cLEc*D$C\\!D<\\P:,_`k5[!cpmHFqRIjFG)]e#`<)GoqpEK*2AI`(eA)ot:no2ER5sJiu+TIW]+sc!W2n)68qGps)Bl]eCn=&/SmT%S4b;hu,#m7%VPb<RLkkjTKRpFPaHW1W3o\'G2XP&-tgmB6FbB`jNp=pk`](;g5SfFB1[#T>YQQONd\'u9&S?hiB>s,4^@fEs*;kEh&k!Kf$G>3:.h@W8VXph71]cMKETU%UV,9rna<1;R).JP-ZI`lYhBU<ne;qStMhC$[dqZnpeoO+@-aX4,R79nlhhI)V9-,i%!s%kK<0m_p.oSG7H\'dst*eG=<3D,taGR60!NI%s]V><=^?jc>$KF+X\'JBuZX8af%<!("e=o^k7V(sQlUN(@D0R7h1MI8lP71f1Csg?[^P-8!+\'Q`d,VC!F@QIl]S-r:,V(>\'Ri$UG)<SgMcr&mC+j1ST2J^h!"t4ps[,CEV)/m["As?">9ddjF<mHN1*n:!@^#MpIr#rJ;i4OoUH$`gu\'mVR>EqcU,_6BMRBU?+eIjV%UMY35M@T`7KHI=X,#p75]CjA$gD+6j<:=XE<pAkR/2C\'S9ORPTGSCP3a&bt4ZD@!Hmat`Ws\'/RlC7ZJ2gGf0S)RuE%RB`R:oD[?]UV\\/Ng6\\6o]%XI\'%dc%KgkWt"%\'rNYeSCAG0j2Hhg&\\Fm"^(7PT@9f\\&c8*&SJZSAk-6&kH?@j^01-NN(n5j*57E.:L"7aN?ljdUC`rkhE,s9Sj%qpbBijc[#d[%];dhuktJ-\\m=7\'Nh;e?.B6*\\+9&7;/IdcNk9aoGHE:=O\\Au/^QJ(pKFKn,_)jD3">:%S(dAYg7\\$W8KO3oORu8o\'??&BsGU)IJO3=2a<tn(dq^F#C_7MA#Ao]@t-a,C*ZIr]LoHdJf)..Y\\#mLX*_\\W>ZDF`Ic/Ll!t-nEH.i[g_k+6Yi-:Tm6=:mYg<pk%-e/I4$OIOq%hq5]&NQn3r6iHOc4t_ErA@%gJ9`qHu+O)n8<U/)79tC`+5CPW\'3B]An:hUJf*55J?-bAPIA4sNWnLdq3\\+QT_=%rgX`5iFi@9%[MX%L`VpR2B?\\\\)cdL`f9?SK>o&RUO)6#%s^dsBQg^9:\'R^dD!`H?`V\\@%9u<^&#%.3,i?pGYcoO&27J4L/WE3\\QELLWUu\\N%tTq3b^uZ*J)q:@Zb!qD#ka1HIu/#a);m)n+V`!3p_it`ZM@R/Z+a?="i7\'\\cfPDGP(8Z>T9&BiuljCYG\\F+NRg\\m[P_E?6S`LO\\N+Rsk`IH=V9b07P$*`CFe5)I^E6>Ik>HO?eKMeS$#TLn^rNETIlXK@/-OM="T$C00p/C7mPZ,:[oGH9$#,]1jH%eJ,acN7.5H43M>^m6c32V\'R>peHio$5PRkD1B%f;T0TbFUDoR:-^+n\\LKpEfFQGDb#TjFb_i0PenW(V@+=1kfu@Z0(Y!Z0B:dk,A8P3m;o)9"Vse="10n!A#*e%G]EHS/pO@N5=+&pjE4c6J\\T5/@g\\B6?@TgZh^Jf!n8n_g4S6W;ZASqB!<Gk?$,]-].S^%87Q\\c9=m_Ir/uDYO7/[Y\'T-bSZsSpc"k=prr"\\STK1]4Y$=qZ(_=Y@4\')^9=09c>r"cQGYd_r,ecaR>r3s$M+9"PJIg\'E=Reu*/ng543:n>/C^PPD%T)+K>9<c:"C=Kb%rM/*B&E<1gcVG;&TV!ZWFCXV?I%\\iPcAk-L)-F8*Lj8G(MXS#C*h\':1b2HnN7@]!u_cJ]X(/6BI%^Be9(%T/bWXUk%FGBG9Yb5)l3n6A!rLSlCJD;:je(N7e3Al,.9Yo*ui_Xfid%fu<!oN+-db$N*n5gZB0HI(0KGK>N:XN[>\'D8:.(f0*;p<b*RMjr_D_aa4g"QqhE=LuPJZk)nu9dBRgClbuhF@$$AKa3Ds.,Z-2PRl]9,d$:"r9Dl2II<h^E5"M^L?P90=920q_Wa?dK_Q2@17`K.VJ[K^,IM0]*VecT/\\6COS`c\'6GNfpf;@Rl-i=:j<K>A&`FVK)-#O#9p8#i8h7q-=Y"6>\'7pj]F[s>gbTREDc7c]f<&8:EP\\6g1q68FkAF(SGk+P2>.ccns,2,R0p4=VFSNSQ.\\l\'FqjcHMps@lr*#QNb9Pjp5cU_jTRiM!"!3runs(")U(U&j^h_R[V3;PVjnU$M8f\\dJoGhCom%.+\\LrS8$>ban!pe=La#9nH.\'>*lD\'\\h4h\\dY4mQZfPt-C7G3#qC&:G!6>-%!N9s`V9>IeppHJQ%"9#Po8p]DO-_A0DlSK,kN@2AC5><iX7RT"Od(ocpsncQYfLbNSI%.7=&\\!9mr8X5M1TUM+d202k9W9?hn/;^q#Pp*T\'t%OZcW"p\'_#_/qbYbdHh45ro?mT4hjg3N+8K@mFF=lR%F4$#Zhc3(Wu8^$MHB0kuj.:q9gLl_=Ai*LV[hF0O[\\:Gql9p:/CU/`^"oL!_Uf43R!l6RSK261M598DD_/W\'8<+g?>-mdg\'2,DZo<T[,OU6fR>o;+hn6Qk_6pNb"]o1n,\\%ZO()7&Y,ia]Ug[d[t)[aXtV?bGC2!EoP1VesE\\R)j0$o0[?j=]QnHS6\'X2c`P/+bd3?;+TUC\'&)Lf7/Qd8Jr\\2A&iTIlV\\Q%2m*9Ir,iD_&T_j+F[c.oR^"QDI[#A+!_>ET8D2$`9_ZUM\'MO4\'pq\\m12fm+B;O-^#CS>+U.<TO[>IJ9\'jrtJY_V,li%<&&eYWd<[X^H[QHg)j7=*+5sJkE/6K@M:8S,g66eK=8GPe0<D@)DYi3mY5D^L(fG.O,`)VC9ba%-400:cOVJ-\'inSNH=<4`1G+;:=6"-[SHg/8\\KI]Gjmbt.?%su(h]D2IF?FOJFfhtH"rk2qZ:4qBj9Nq]_\\s]/8=XTI1iMl2BXG$8`*C:I0DtJne4\\;S;*LEI[n^FJ<-_&YW0#?O&dY6t]KskqA"]k8$`R/C`O;Z0IL%@>9Fh[$m<?dZ58VU6OlL*:,qPB5>I9\'c`H&2$$grpUA4YA/pGu-1R2.-25Q0aY,XLY&F$*!MY19lDOEh!CE:Fh*OXMlRV3[am[+>DFg2Fr_cIo#_oen%=T2VBWj\'+71U1A-RC5H[DdkXF.)=C<.YpK?+$E+-X`A$#*om[$V44.Nb(X_b4+Q;cI&2ARJ]\\cgqS\\YjAmf8J%n]d8^gl40Oj$BpL;6.)WK7bM7!u/Br-aNSdrD\'=9WFI@bl72`/05I#.9D`VZcu5^A&njUJEqH?4q5E,rd[l=Sbuo>%_"&/B8_@hBQ7g78KfDQt.90,KM<Jl%^LrlkFRZ.nT,$C!U>*/YP##p,?r1+<C,F0gL`5!mI!8WX^QiUQG6d<L):!2/"t)7?+!#G%iU%C26CBC`NR,cuUSfJ0<6BRW/5.>D>6K!ahEFhX1d+$rLlb3AYM(!17kui.\\/6-L>Z>AFo(I$o4XjJ$$5ctq/US+MX>t3Qkco&0@H0i@5?S-;qaM+kDK<1Lou39Mg/eCrZqeCB!\\(ZZSL&\\NM)_RU=Y\\?c*Bm_L?SMmJ\'cHWOEV]2kWQ(<LKD)+f#>1Lkz*FuOI0MaXH!!0nhonNPJaEsm%Z,C;P!WW3#!!HG.'
	exec(lzma.decompress(base64.a85decode(_SRC_B85)).decode("utf-8"), multiCMD.__dict__)

try:
	import functools
	import typing
	# Check if functiools.cache is available
	# cache_decorator = functools.cache
	def cache_decorator(user_function):
		def _make_hashable(item):
			if isinstance(item, typing.Mapping):
				# Sort items so that {'a':1, 'b':2} and {'b':2, 'a':1} hash the same
				return tuple(
					( _make_hashable(k), _make_hashable(v) )
					for k, v in sorted(item.items(), key=lambda item: item[0])
				)
			if isinstance(item, (list, set, tuple)):
				return tuple(_make_hashable(e) for e in item)
			# Fallback: assume item is already hashable
			return item
		def decorating_function(user_function):
			# Create the real cached function
			cached_func = functools.lru_cache(maxsize=None)(user_function)
			@functools.wraps(user_function)
			def wrapper(*args, **kwargs):
				# Convert all args/kwargs to hashable equivalents
				hashable_args = tuple(_make_hashable(a) for a in args)
				hashable_kwargs = {
					k: _make_hashable(v) for k, v in kwargs.items()
				}
				# Call the lru-cached version
				return cached_func(*hashable_args, **hashable_kwargs)
			# Expose cache statistics and clear method
			wrapper.cache_info = cached_func.cache_info
			wrapper.cache_clear = cached_func.cache_clear
			return wrapper
		return decorating_function(user_function)
except Exception:
	import sys
	# If lrucache is not available, use a dummy decorator
	print('Warning: functools.lru_cache is not available, multiSSH3 will run slower without cache.',file=sys.stderr)
	def cache_decorator(func):
		return func

version = '1.36'
VERSION = version
__version__ = version
COMMIT_DATE = '2025-12-11'

SMARTCTL_PATH = shutil.which("smartctl")

def read_text(path):
	try:
		with open(path, "r", encoding="utf-8", errors="ignore") as f:
			return f.read().strip()
	except Exception:
		return None

def read_int(path):
	s = read_text(path)
	if s is None:
		return 0
	try:
		return int(s)
	except Exception:
		return 0

def build_symlink_dict(dir_path):
	"""
	Build map: devname -> token (uuid or label string) using symlinks under
	/dev/disk/by-uuid or /dev/disk/by-label.
	"""
	mapping = {}
	if not os.path.isdir(dir_path):
		return mapping
	try:
		for entry in os.listdir(dir_path):
			p = os.path.join(dir_path, entry)
			try:
				if os.path.islink(p):
					tgt = os.path.realpath(p)
					mapping.setdefault(tgt, entry)
			except Exception:
				continue
	except Exception:
		pass
	return mapping

def get_statvfs_use_size(mountpoint):
	try:
		st = os.statvfs(mountpoint)
		block_size = st.f_frsize if st.f_frsize > 0 else st.f_bsize
		total = st.f_blocks * block_size
		avail = st.f_bavail * block_size
		used = total - avail
		return total, used
	except Exception:
		return 0, 0

@cache_decorator
def read_discard_support(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return 'N/A'
	dmbytes = read_int(os.path.join(sysfs_block_path, "queue", "discard_max_bytes"))
	try:
		if dmbytes > 0:
			return 'Yes'
		else:
			return 'No'
	except Exception:
		return 'N/A'

@cache_decorator
def get_real_sysfs_device_path(sysfs_block_path):
	"""
	Return the sysfs 'device' directory for this block node (resolves partition
	to its parent device as well).
	"""
	dev_link = os.path.join(sysfs_block_path, "device")
	try:
		return os.path.realpath(dev_link)
	except Exception:
		return dev_link

@cache_decorator
def read_model_and_serial(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return '', ''
	device_path = get_real_sysfs_device_path(sysfs_block_path)
	model = read_text(os.path.join(device_path, "model"))
	serial = read_text(os.path.join(device_path, "serial"))
	if serial is None:
		serial = read_text(os.path.join(device_path, "wwid"))
	if model:
		model = " ".join(model.split())
	else:
		model = ''
	if serial:
		serial = " ".join(serial.split())
	else:
		serial = ''
	return model, serial

def read_size(sysfs_block_path):# -> tuple[int | None, Any] | Literal['']:
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return 0
	sectors = read_int(os.path.join(sysfs_block_path, "size"))
	return sectors * 512 # linux kernel uses 512 byte sectors

MountEntry = namedtuple("MountEntry", ["MOUNTPOINT", "FSTYPE", "OPTIONS"])
def parseMount():
	rtn = multiCMD.run_command('mount',timeout=1,quiet=True)
	mount_table = defaultdict(list)
	for line in rtn:
		device_name, _, line = line.partition(' on ')
		if device_name.startswith(os.path.sep):
			device_name = os.path.realpath(device_name)
		mount_point, _, line = line.partition(' type ')
		fstype, _ , options = line.partition(' (')
		options = options.rstrip(')').split(',')
		mount_table[device_name].append(MountEntry(mount_point, fstype, options))
	return mount_table

def get_blocks():
	# get entries in /sys/class/block
	block_devices = []
	for entry in os.listdir("/sys/class/block"):
		if os.path.isdir(os.path.join("/sys/class/block", entry)):
			block_devices.append(f'/dev/{entry}')
	return block_devices

@cache_decorator
def is_block_device(devpath):
	try:
		st_mode = os.stat(devpath).st_mode
		return stat.S_ISBLK(st_mode)
	except Exception:
		return False

def is_partition(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return False
	return os.path.exists(os.path.join(sysfs_block_path, "partition"))

@cache_decorator
def get_partition_parent_name(name):
	if not name:
		return None
	name = os.path.basename(name)
	sysfs_block_path = os.path.realpath(os.path.join('/sys/class/block', name))
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return None
	part_file = os.path.join(sysfs_block_path, "partition")
	if not os.path.exists(part_file):
		return os.path.join('/dev', name) if is_block_device(os.path.join('/dev', name)) else None
	parent = os.path.basename(os.path.dirname(sysfs_block_path))
	return os.path.join('/dev', parent) if parent and parent != name else None

@cache_decorator
def get_sector_size(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return 512
	if get_partition_parent_name(sysfs_block_path):
		sysfs_block_path = os.path.join('/sys/class/block', os.path.basename(get_partition_parent_name(sysfs_block_path)))
	sector_size = read_int(os.path.join(sysfs_block_path, "queue", "hw_sector_size"))
	if sector_size == 0:
		sector_size = read_int(os.path.join(sysfs_block_path, "queue", "logical_block_size"))
	return sector_size if sector_size else 512

def get_read_write_rate_throughput_iter(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		while True:
			yield 0, 0
	rx_path = os.path.join(sysfs_block_path, "stat")
	start_time = time.monotonic()
	sector_size = get_sector_size(sysfs_block_path)
	previous_bytes_read = 0
	previous_bytes_written = 0
	try:
		with open(rx_path, "r", encoding="utf-8", errors="ignore") as f:
			fields = f.read().strip().split()
		if len(fields) < 7:
			yield 0, 0
		sectors_read = int(fields[2])
		read_time = int(fields[3]) / 1000.0
		sectors_written = int(fields[6])
		write_time = int(fields[7]) / 1000.0
		read_throughput = (sectors_read * sector_size) / read_time if read_time > 0 else 0
		write_throughput = (sectors_written * sector_size) / write_time if write_time > 0 else 0
		previous_bytes_read = sectors_read * sector_size
		previous_bytes_written = sectors_written * sector_size
		yield int(read_throughput), int(write_throughput)
	except Exception:
		yield 0, 0
	while True:
		try:
			with open(rx_path, "r", encoding="utf-8", errors="ignore") as f:
				fields = f.read().strip().split()
			if len(fields) < 7:
				yield 0, 0
			# fields: https://www.kernel.org/doc/html/latest/block/stat.html
			# 0 - reads completed successfully
			# 1 - reads merged
			# 2 - sectors read
			# 3 - time spent reading (ms)
			# 4 - writes completed
			# 5 - writes merged
			# 6 - sectors written
			# 7 - time spent writing (ms)
			# 8 - I/Os currently in progress
			# 9 - time spent doing I/Os (ms)
			# 10 - weighted time spent doing I/Os (ms)
			sectors_read = int(fields[2])
			sectors_written = int(fields[6])
			bytes_read = sectors_read * sector_size
			bytes_written = sectors_written * sector_size
			end_time = time.monotonic()
			elapsed_time = end_time - start_time
			start_time = end_time
			read_throughput = (bytes_read - previous_bytes_read) / elapsed_time if elapsed_time > 0 else 0
			write_throughput = (bytes_written - previous_bytes_written) / elapsed_time if elapsed_time > 0 else 0
			previous_bytes_read = bytes_read
			previous_bytes_written = bytes_written
			yield int(read_throughput), int(write_throughput)
		except Exception:
			yield 0, 0

ALL_OUTPUT_FIELDS = ["NAME", "FSTYPE", "SIZE", "FSUSE%", "MOUNTPOINT", "SMART", "LABEL", "UUID", "MODEL", "SERIAL", "DISCARD", "READ", "WRITE"]

# DRIVE_INFO = namedtuple("DRIVE_INFO", 
# 	["NAME", "FSTYPE", "SIZE", "FSUSEPCT", "MOUNTPOINT", "SMART","RTPT",'WTPT', "LABEL", "UUID", "MODEL", "SERIAL", "DISCARD"])
def get_drives_info(print_bytes = False, use_1024 = False, mounted_only=False, best_only=False, 
					formated_only=False, show_zero_size_devices=False,pseudo=False,tptDict = {},
					full=False,active_only=False,output="all",exclude="",
					filter_patterns=None,invert_match=False,match_devname_only=False,timeout=None):
	global SMARTCTL_PATH
	global ALL_OUTPUT_FIELDS
	if output == "all":
		output_fields = ALL_OUTPUT_FIELDS
	else:
		output_fields = [x.strip().upper() for x in output.split(',')]
		for field in output_fields:
			if field not in ALL_OUTPUT_FIELDS:
				print(f"Ignoring invalid output field: {field}.", file=sys.stderr)
				output_fields.remove(field)
	if exclude:
		exclude_fields = [x.strip().upper() for x in exclude.split(',')]
		for field in exclude_fields:
			if field in output_fields:
				output_fields.remove(field)
	if not output_fields:
		print("No valid output fields specified.", file=sys.stderr)
		return []
	output_list = [output_fields]
	output_fields_set = set(output_fields)
	if {'SIZE','FSTYPE','UUID','LABEL'}.intersection(output_fields_set):
		lsblk_result = multiCMD.run_command('lsblk -brnp -o NAME,SIZE,FSTYPE,UUID,LABEL',timeout=timeout,quiet=True,wait_for_return=False,return_object=True)
	block_devices = get_blocks()
	smart_infos = {}
	for block_device in block_devices:
		if 'SMART' in output_fields_set and SMARTCTL_PATH:
			parent_name = get_partition_parent_name(block_device)
			if parent_name:
				if parent_name not in smart_infos:
					smart_infos[parent_name] = multiCMD.run_command(f'{SMARTCTL_PATH} -H {parent_name}',timeout=timeout,quiet=True,wait_for_return=False,return_object=True)
		if block_device not in tptDict:
			sysfs_block_path = os.path.join('/sys/class/block', os.path.basename(block_device))
			tptDict[block_device] = get_read_write_rate_throughput_iter(sysfs_block_path)
	mount_table = parseMount()
	target_devices = set(block_devices)
	if pseudo:
		target_devices.update(mount_table.keys())
	if filter_patterns and match_devname_only:
		pattern = re.compile('|'.join(filter_patterns))
		filtered_devices = set()
		for device in target_devices:
			match = pattern.search(device)
			if (match and not invert_match) or (not match and invert_match):
				filtered_devices.add(device)
		target_devices = filtered_devices
	target_devices = sorted(target_devices)
	uuid_dict = {}
	if 'UUID' in output_fields_set:
		uuid_dict = build_symlink_dict("/dev/disk/by-uuid")
	label_dict = {}
	if 'LABEL' in output_fields_set:
		label_dict = build_symlink_dict("/dev/disk/by-label")
	fstype_dict = {}
	size_dict = {}
	if {'SIZE','FSTYPE','UUID','LABEL'}.intersection(output_fields_set):
		lsblk_result.thread.join()
		if lsblk_result.returncode == 0:
			for line in lsblk_result.stdout:
				lsblk_name, lsblk_size, lsblk_fstype, lsblk_uuid, lsblk_label = line.split(' ', 4)
				if lsblk_name.startswith(os.path.sep):
					lsblk_name = os.path.realpath(lsblk_name)
				# the label can be \x escaped, we need to decode it
				if 'UUID' in output_fields_set:
					lsblk_uuid = bytes(lsblk_uuid, "utf-8").decode("unicode_escape")
					if lsblk_uuid:
						uuid_dict[lsblk_name] = lsblk_uuid
				if 'FSTYPE' in output_fields_set:
					lsblk_fstype = bytes(lsblk_fstype, "utf-8").decode("unicode_escape")
					if lsblk_fstype:
						fstype_dict[lsblk_name] = lsblk_fstype
				if 'LABEL' in output_fields_set:
					lsblk_label = bytes(lsblk_label, "utf-8").decode("unicode_escape")
					if lsblk_label:
						label_dict[lsblk_name] = lsblk_label
				if 'SIZE' in output_fields_set:
					try:
						size_dict[lsblk_name] = int(lsblk_size)
					except Exception:
						pass
	for device_name in target_devices:
		if mounted_only and device_name not in mount_table:
			continue
		if active_only and device_name not in tptDict:
			continue
		device_properties = defaultdict(str)
		device_properties['NAME'] = device_name if full else device_name.replace('/dev/', '')
		# fstype, size, fsuse%, mountpoint, rtpt, wtpt, lable, uuid are partition specific
		# smart, model, serial, discard are device specific, and only for block devices
		# fstype, size, fsuse%, mountpoint does not require block device and can have multiple values per device
		if is_block_device(device_name):
			parent_name = get_partition_parent_name(device_name)
			parent_sysfs_path = os.path.realpath(os.path.join('/sys/class/block', os.path.basename(parent_name))) if parent_name else None
			if 'MODEL' in output_fields_set or 'SERIAL' in output_fields_set:
				device_properties['MODEL'], device_properties['SERIAL'] = read_model_and_serial(parent_sysfs_path)
			if 'DISCARD' in output_fields_set:
				device_properties['DISCARD'] = read_discard_support(parent_sysfs_path)
			if parent_name in smart_infos and SMARTCTL_PATH:
				smart_info_obj = smart_infos[parent_name]
				smart_info_obj.thread.join()
				for line in smart_info_obj.stdout:
					line = line.lower()
					if "health" in line:
						smartinfo = line.rpartition(':')[2].strip().upper()
						device_properties['SMART'] = smartinfo.replace('PASSED', 'OK')
						break
					elif "denied" in line:
						device_properties['SMART'] = 'DENIED'
						break
			#size_bytes = read_size(os.path.join('/sys/class/block', os.path.basename(device_name)))
		if device_name in tptDict:
			try:
				device_properties['READ'], device_properties['WRITE'] = next(tptDict[device_name])
				if active_only and device_properties['READ'] == 0 and device_properties['WRITE'] == 0:
					continue
				if print_bytes:
					device_properties['READ'] = str(device_properties['READ'])
					device_properties['WRITE'] = str(device_properties['WRITE'])
				else:
					device_properties['READ'] = multiCMD.format_bytes(device_properties['READ'], use_1024_bytes=use_1024, to_str=True,str_format='.0f') + 'B/s'
					device_properties['WRITE'] = multiCMD.format_bytes(device_properties['WRITE'], use_1024_bytes=use_1024, to_str=True,str_format='.0f') + 'B/s'
			except Exception:
				device_properties['READ'] = ''
				device_properties['WRITE'] = ''
		if device_name in label_dict:
			device_properties['LABEL'] = label_dict[device_name]
		if device_name in uuid_dict:
			device_properties['UUID'] = uuid_dict[device_name]
		mount_points = mount_table.get(device_name, [])
		if best_only:
			if mount_points:
				mount_points = [sorted(mount_points, key=lambda x: len(x.MOUNTPOINT))[0]]
		if mount_points:
			for mount_entry in mount_points:
				device_properties['FSTYPE'] = mount_entry.FSTYPE
				if formated_only and not device_properties['FSTYPE']:
					continue
				device_properties['MOUNTPOINT'] = mount_entry.MOUNTPOINT
				size_bytes, used_bytes = get_statvfs_use_size(device_properties['MOUNTPOINT'])
				if size_bytes == 0 and not show_zero_size_devices:
					continue
				device_properties['FSUSE%'] = f"{int(round(100.0 * used_bytes / size_bytes))}%" if size_bytes > 0 else "N/A"
				if print_bytes:
					device_properties['SIZE'] = str(size_bytes)
				else:
					device_properties['SIZE'] = multiCMD.format_bytes(size_bytes, use_1024_bytes=use_1024, to_str=True) + 'B'
				output_list.append([device_properties[output_field] for output_field in output_fields])
		else:
			if formated_only and device_name not in fstype_dict:
				continue
			device_properties['FSTYPE'] = fstype_dict.get(device_name, '')
			size_bytes = size_dict.get(device_name, read_size(os.path.join('/sys/class/block', os.path.basename(device_name))))
			if size_bytes == 0 and not show_zero_size_devices:
				continue
			if print_bytes:
				device_properties['SIZE'] = str(size_bytes)
			else:
				device_properties['SIZE'] = multiCMD.format_bytes(size_bytes, use_1024_bytes=use_1024, to_str=True) + 'B'
			output_list.append([device_properties[output_field] for output_field in output_fields])
		multiCMD.join_threads(timeout=timeout)
	if not match_devname_only:
		if filter_patterns:
			pattern = re.compile('|'.join(filter_patterns))
			filtered_output_list = [output_list[0]]  # include header
			for row in output_list[1:]:
				match = any(pattern.search(field) for field in row)
				if (match and not invert_match) or (not match and invert_match):
					filtered_output_list.append(row)
			output_list = filtered_output_list
		elif invert_match:
			# if no patterns but invert_match is set, return only header
			output_list = [output_list[0]]
	return output_list


def main():
	parser = argparse.ArgumentParser(description="Gather disk and partition info for block devices.")
	parser.add_argument('-j','--json', help="Produce JSON output", action="store_true")
	parser.add_argument('-b','--bytes', help="Print the SIZE column in bytes rather than in a human-readable format", action="store_true")
	parser.add_argument('-H','--si', help="Use powers of 1000 not 1024 for SIZE column", action="store_true")
	parser.add_argument('-F','-fo','--formated_only', help="Show only formated filesystems", action="store_true")
	parser.add_argument('-M','-mo','--mounted_only', help="Show only mounted filesystems", action="store_true")
	parser.add_argument('-B','-bo','--best_only', help="Show only shortest mount point for each device", action="store_true")
	parser.add_argument('-A','-ao','--active_only', help="Show only active devices (positive read/write activity)", action="store_true")
	parser.add_argument('-R','--full', help="Show full device information, do not collapse drive info when length > console length", action="store_true")
	parser.add_argument('-P','--pseudo', help="Include pseudo file systems as well (tmpfs / nfs / cifs etc.)", action="store_true")
	parser.add_argument('-o','--output', help="Specify which output columns to print.Use comma to separate columns. default: all available", default="all", type=str)
	parser.add_argument('-x','--exclude', help="Specify which output columns to exclude.Use comma to separate columns. default: none", default="", type=str)
	parser.add_argument('-t','--timeout', help="Set command timeout in seconds (default: 2)", default=2, type=int)
	parser.add_argument('--show_zero_size_devices', help="Show devices with zero size", action="store_true")
	parser.add_argument('-D','--match_devname_only', help="Change filter pattern to match just the device names instead of the full line", action="store_true")
	parser.add_argument('-v','--invert_match', help="Invert the filter match", action="store_true")
	parser.add_argument('filter_patterns', nargs='*', help="Filter pattern(s) to match (e.g., sda, nvme0n1p1, btrfs). If specified, only devices matching any of the patterns will be shown. Will prioritize print_period first thus if wanting to filter a number and do not repeat, append a 0 (zero) at the end.")
	parser.add_argument('print_period', nargs='?', default=0, type=int, help="If specified as a non zero number, repeat the output every N seconds")
	parser.add_argument('-V', '--version', action='version', version=f"%(prog)s {version} @ {COMMIT_DATE} stat drives by pan@zopyr.us")

	args = parser.parse_args()
	tptDict = {}
	if not args.print_period:
		if args.filter_patterns:
			try:
				args.print_period = int(args.filter_patterns[-1])
				args.filter_patterns = args.filter_patterns[:-1]
			except Exception:
				pass
	while True:
		results = get_drives_info(print_bytes = args.bytes, use_1024 = not args.si, 
							mounted_only=args.mounted_only, best_only=args.best_only, 
							formated_only=args.formated_only, show_zero_size_devices=args.show_zero_size_devices,
							pseudo=args.pseudo,tptDict=tptDict,full=args.full,active_only=args.active_only,
							output=args.output,exclude=args.exclude,
							filter_patterns=args.filter_patterns,invert_match=args.invert_match,match_devname_only=args.match_devname_only,
							timeout=args.timeout,
							)
		if args.json:
			import json
			print(json.dumps(results, indent=1),flush=True)
		else:
			print(multiCMD.pretty_format_table(results,full=args.full),flush=True)
		if args.print_period > 0:
			try:
				time.sleep(args.print_period)
				args.active_only = True
			except KeyboardInterrupt:
				break
		else:
			break


if __name__ == "__main__":
	main()