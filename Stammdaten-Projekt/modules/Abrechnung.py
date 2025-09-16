############################################################################
# 1.0.0
# Lohnverrechnungstool für das Jahr 2025
# Dient als Brutto-Netto-Rechner im Terminal
# Hauptkennwerte für das Jahr 2025 via globaler Variablen implementiert
############################################################################

import datetime

# ANSI Escape-Sequenzen für Farben & Formatierung
RED = "\033[91m"       # Rote Farbe
GREEN = "\033[92m"     # Grüne Farbe
BOLD = "\033[1m"       # Fett
RESET = "\033[0m"      # Zurücksetzen auf Standardfarbe

SV_DG_PROZENT = 0.2038
SV_DG_IE_PROZENT = 0.001
SV_DG_WB_PROZENT = 0.005
SV_DN_GRENZE_0 = 2074.0
SV_DN_GRENZE_1 = 2262.0
SV_DN_GRENZE_2 = 2451.0
#SV_DN_GRENZE_3 = 
SV_DN_PROZENT_0 = 0.1412
SV_DN_PROZENT_1 = 0.1512
SV_DN_PROZENT_2 = 0.1612
SV_DN_PROZENT_3 = 0.1707
SV_DN_AK_PROZENT = 0.005
SV_DN_WB_PROZENT = 0.005
SV_DN_MBV_PROZENT = 0.0153
SV_HBGL = 6450.0

LST_68_1 = 400.
LST_68_2_STUNDEN = 18.
LST_68_2_WERT = 200.

DGA_WIEN = 2.

KOMM_ST_PROZENT = 0.03
DB_PROZENT = 0.037
DBZ_PROZENT = 0.0036

LST_SZ_FREI = 620.
LST_SZ_1 = 24380.
LST_SZ_2 = 49380.
LST_SZ_3 = 83333.
LST_SZ_1_PROZENT = 0.06
LST_SZ_2_PROZENT = 0.27
LST_SZ_3_PROZENT = 0.3575

LST_AVAB_1K = 50.08
LST_AVAB_2K = 67.75
LST_AVAB_3KUND = 22.33

FABO_U18G = 166.68
FABO_U18H = 83.34
FABO_UE18G = 58.34
FABO_UE18H = 29.17
LST_VAB = 40.58

LST_ST1 = 1120.
LST_ST2 = 1812.45
LST_ST3 = 2997.33
LST_ST4 = 5774.83
LST_ST5 = 8600.33
LST_ST6 = 83344.33

LST_ST1_PROZENT = 0.
LST_ST2_PROZENT = 0.20
LST_ST3_PROZENT = 0.3
LST_ST4_PROZENT = 0.4
LST_ST5_PROZENT = 0.48
LST_ST6_PROZENT = 0.5
LST_ST7_PROZENT = 0.55

LST_ST2_ABZUG = 224.
LST_ST3_ABZUG = 405.24
LST_ST4_ABZUG = 704.94
LST_ST5_ABZUG = 1166.96
LST_ST6_ABZUG = 1338.97
LST_ST7_ABZUG = 5506.19

OEGB_PROZENT = 0.01
OEGB_GRENZWERT = 40.8

def count_mondays_in_month(year, month):
    count = 0
    for day in range(1, 32):  # Loop through days 1 to 31
        try:
            if datetime.date(year, month, day).weekday() == 0:  # 0 is Monday
                count += 1
        except ValueError:
            break  # Break if the day is invalid for the month
    return count

def calc_brutto2netto(monat : int, jahr : int, stundensatz : float, brutto : float, mehrstunden0 : float = 0., mehrstunden25 : float = 0., mehrstunden50 : float = 0., überstunden50 : float = 0., überstunden100 : float = 0., sonderzahlungen : float = 0., sachbezug : float = 0., diäten : float = 0., reisekosten : float = 0., freibetragsbescheid : float = 0., pendlerpauschale : float = 0., pendlereuro = 0., anzahl_Kinder_AVAB : int = 0, anspruch_fabo : bool = False, gewerkschaftmitglied : bool = False, jahressechstel : float = 0.):
    """
    Berechnet das Netto-Gehalt anhand der gegebenen Parameter
    Einige dieser Parameter sind optional, da selten gebraucht, wichtig ist vor allem aber Monat/Jahr, Stundensatz und Brutto-Gehalt
    Args:
        monat (int): Monat der abgerechnet werden soll.
        jahr (int): Jahr das abgerechnet werden soll
        stundensatz (float): Stundensatz (Stunden/Woche) die der Mitarbeiter arbeitet
        brutto (float): Bruttoverdienst des Mitarbeiters im Monat
        mehrstunden0 (float, optional): Anzahl der Mehrstunden mit 0% Zuschlag. Defaults to 0..
        mehrstunden25 (float, optional): Anzahl der Mehrstunden mit 25%. Defaults to 0..
        mehrstunden50 (float, optional): Anzahl der Mehrstunden mit 50%. Defaults to 0..
        sonderzahlungen (float, optional): Sonderzahlung des Dienstnehmers (Urlaubsbeihilfe & Weinachtsrenumeration). Defaults to 0..
        sachbezug (float, optional): Sachbezüge die der Mitarbeiter erhält (in €). Defaults to 0..
        reisekosten (float, optional): Reisekosten die zu berücksichtigen sind (in €). Defaults to 0..
        freibetragsbescheid (float, optional): Freibetragsbescheid den der Mitarbeiter gemeldet hat (in €). Defaults to 0..
        pendlerpauschale (float, optional): Pendlerpauschale lt Pendlerrechner https://pendlerrechner.bmf.gv.at/ (in €/Monat). Defaults to 0..
        pendlereuro (_type_, optional): Pendlereuro lt. https://pendlerrechner.bmf.gv.at/ (in €/Monat). Defaults to 0..
        anzahl_Kinder_AVAB (int, optional): Anzahl der Kinder für die Aleinerzieherabsetzbetrag bezogen werden soll. Defaults to 0.
        anspruch_fabo (bool, optional): Soll der Familienbonus Plus berechnet werden?. Defaults to False.
        gewerkschaftmitglied (bool, optional): Ist der Mitarbeiter in der Gewerkschaft?. Defaults to False.
        jahressechstel (float, optional): Jahressechstel (Summe der Bruttobezüge des Jahres durch die bisher ausbezahlten Monate). Defaults to 0..
    """
    

    teiler1 = 1/(4.33*stundensatz)
    teiler2 = 1./143. / (stundensatz/38.5)

    brlohn = brutto + mehrstunden0*(brutto*teiler1)*(1.+0.0)

    brlohn = brlohn + mehrstunden25*(brutto*teiler1)*(1.+0.25)

    brlohn = brlohn + mehrstunden50*(brutto*teiler1)*(1.+0.5)

    ü50grund = überstunden50*(brutto*teiler2)
    ü50zuschl = überstunden50*(brutto*teiler2)*0.5
    brlohn = brlohn + ü50grund + ü50zuschl

    ü100grund = überstunden100*(brutto*teiler2)
    ü100zuschl = überstunden100*(brutto*teiler2)
    brlohn = brlohn + ü100grund + ü100zuschl

    sv_bmg = brlohn + sachbezug

    brlohn = brlohn + diäten

    brlohn = brlohn + reisekosten

    dienstg_sv = sv_bmg*(SV_DG_PROZENT+SV_DG_IE_PROZENT+SV_DG_WB_PROZENT)

    if sv_bmg < SV_DN_GRENZE_0:
        sv = sv_bmg * (SV_DN_PROZENT_0 + SV_DN_AK_PROZENT + SV_DN_WB_PROZENT)
    elif sv_bmg < SV_DN_GRENZE_1:
        sv = sv_bmg * (SV_DN_PROZENT_1 + SV_DN_AK_PROZENT + SV_DN_WB_PROZENT)
    elif sv_bmg < SV_DN_GRENZE_2:
        sv = sv_bmg * (SV_DN_PROZENT_2 + SV_DN_AK_PROZENT + SV_DN_WB_PROZENT)
    elif sv_bmg > SV_HBGL:
        sv = SV_HBGL*(SV_DN_PROZENT_3 + SV_DN_AK_PROZENT + SV_DN_WB_PROZENT)
        dienstg_sv = SV_HBGL*0.2123
    else:
        sv = sv_bmg*(SV_DN_PROZENT_3 + SV_DN_AK_PROZENT + SV_DN_WB_PROZENT)

    lnk_bmg = brlohn - diäten - reisekosten + sachbezug + sonderzahlungen

    kommst = lnk_bmg*KOMM_ST_PROZENT
    db = lnk_bmg*DB_PROZENT
    dz = lnk_bmg*DBZ_PROZENT

    BV = (sv_bmg + sonderzahlungen)*SV_DN_MBV_PROZENT

    dga = count_mondays_in_month(year=jahr, month=monat) * DGA_WIEN

    if sachbezug != 0.0:
        pr20 = brlohn*0.2

        if sv_bmg < SV_DN_GRENZE_0:
            svtemp = sv_bmg * SV_DN_PROZENT_0
        elif sv_bmg < SV_DN_GRENZE_1:
            svtemp = sv_bmg * SV_DN_PROZENT_1
        elif sv_bmg < SV_DN_GRENZE_2:
            svtemp = sv_bmg * SV_DN_PROZENT_2
        elif sv_bmg > SV_HBGL:
            svtemp = SV_HBGL*SV_DN_PROZENT_3
        else:
            svtemp = sv_bmg*SV_DN_PROZENT_3
        
        if svtemp > pr20:
            
            dienstg_sv = dienstg_sv + svtemp - pr20
            if sv_bmg <= SV_HBGL:
                sv = pr20 + sv_bmg*(SV_DN_AK_PROZENT+SV_DN_WB_PROZENT)
            else:
                sv = pr20 + SV_HBGL*(SV_DN_AK_PROZENT+SV_DN_WB_PROZENT)


    if sonderzahlungen != 0.:

        altesonder = float(input("Gib das Brutto der Sonderzahlungen des bisherigen Jahres ein:\n"))

        if (altesonder + sonderzahlungen) > (2.*SV_HBGL):
            restsonder = (2.*SV_HBGL) - altesonder
            if restsonder > 0.0:
                if sonderzahlungen < SV_DN_GRENZE_0:
                    prsvsonder = SV_DN_PROZENT_0
                    svsonder = restsonder * SV_DN_PROZENT_0
                elif sonderzahlungen < SV_DN_GRENZE_1:
                    prsvsonder = SV_DN_PROZENT_1
                    svsonder = restsonder * SV_DN_PROZENT_1
                elif sonderzahlungen < SV_DN_GRENZE_2:
                    prsvsonder = SV_DN_PROZENT_2
                    svsonder = restsonder * SV_DN_PROZENT_2
                else:
                    prsvsonder = SV_DN_PROZENT_3
                    svsonder = restsonder*SV_DN_PROZENT_3
        else:

            if sonderzahlungen < SV_DN_GRENZE_0:
                prsvsonder = SV_DN_PROZENT_0
                svsonder = sonderzahlungen * SV_DN_PROZENT_0
            elif sonderzahlungen < SV_DN_GRENZE_1:
                prsvsonder = SV_DN_PROZENT_1
                svsonder = sonderzahlungen * SV_DN_PROZENT_1
            elif sonderzahlungen < SV_DN_GRENZE_2:
                prsvsonder = SV_DN_PROZENT_2
                svsonder = sonderzahlungen * SV_DN_PROZENT_2
            elif sonderzahlungen > (2.*SV_HBGL):
                prsvsonder = SV_DN_PROZENT_3
                svsonder = (2.*SV_HBGL)*SV_DN_PROZENT_3
            else:
                prsvsonder = SV_DN_PROZENT_3
                svsonder = sonderzahlungen*SV_DN_PROZENT_3
    else:
        svsonder = 0.

    dienstg_svsonder = sonderzahlungen*(SV_DG_PROZENT+SV_DG_IE_PROZENT)

    if anzahl_Kinder_AVAB == 1:
        av = LST_AVAB_1K
    elif anzahl_Kinder_AVAB == 2:
        av = LST_AVAB_2K
    elif anzahl_Kinder_AVAB > 2:
        av = LST_AVAB_2K + LST_AVAB_3KUND*(anzahl_Kinder_AVAB-2)
    else:
        av = 0.

    FaBoP = 0.0
    if anspruch_fabo == True:
        u18g = int(input("Wie viele Kinder unter 18 mit ganzem Anspruch? (Anzahl)\n"))
        u18h= int(input("Wie viele Kinder unter 18 mit halbem Anspruch? (Anzahl)\n"))
        ü18g = int(input("Wie viele Kinder über 18 mit ganzem Anspruch? (Anzahl)\n"))
        ü18h = int(input("Wie viele Kinder über 18 mit halbem Anspruch? (Anzahl)\n"))

        FaBoP = u18g * FABO_U18G + u18h * FABO_U18H + ü18g * FABO_UE18G + ü18h * FABO_UE18H

    if gewerkschaftmitglied:
        ÖGB_wert = brlohn*OEGB_PROZENT
        if ÖGB_wert > OEGB_GRENZWERT:
            ÖGB_wert = OEGB_GRENZWERT
    else:
        ÖGB_wert = 0.

    ü50zuschl_st = ü50zuschl
    ü100zuschl_st = ü100zuschl
    if überstunden50 > LST_68_2_STUNDEN:
        ü50zuschl_st = ü50zuschl/überstunden50*LST_68_2_STUNDEN
    if ü50zuschl > LST_68_2_WERT:
        ü50zuschl_st = LST_68_2_WERT

    if ü100zuschl > LST_68_1:
        ü100zuschl_st = LST_68_1

    lst_bmg = brlohn + sachbezug - sv - freibetragsbescheid - pendlerpauschale - ü50zuschl_st - ü100zuschl_st - diäten - reisekosten - ÖGB_wert

    if sonderzahlungen != 0.:
        
        if altesonder != 0.0:
            
            if altesonder < jahressechstel:
                sv_sb_teil1 = altesonder * prsvsonder
                rest_altsonder_sv = altesonder - sv_sb_teil1

                rest_altsonder_sv = max(rest_altsonder_sv - LST_SZ_FREI, 0.0)

                if rest_altsonder_sv < LST_SZ_1:
                    
                    altsonder_sv = rest_altsonder_sv*LST_SZ_1_PROZENT
                    restSB_pr = LST_SZ_1_PROZENT
                    restSB_lstbmg = LST_SZ_1 - rest_altsonder_sv

                elif rest_altsonder_sv < LST_SZ_2:

                    altsonder_sv = LST_SZ_1*LST_SZ_1_PROZENT + (rest_altsonder_sv-LST_SZ_1)*LST_SZ_2_PROZENT
                    restSB_pr = LST_SZ_2_PROZENT
                    restSB_lstbmg = LST_SZ_2 - rest_altsonder_sv

                elif rest_altsonder_sv < (LST_SZ_3-LST_SZ_FREI):

                    altsonder_sv = LST_SZ_1*LST_SZ_1_PROZENT + (LST_SZ_2-LST_SZ_1)*LST_SZ_2_PROZENT + (rest_altsonder_sv-LST_SZ_2)*LST_SZ_3_PROZENT
                    restSB_pr = LST_SZ_3_PROZENT
                    restSB_lstbmg = (LST_SZ_3-LST_SZ_FREI) - rest_altsonder_sv

                else:

                    altsonder_sv = LST_SZ_1*LST_SZ_1_PROZENT + (LST_SZ_2-LST_SZ_1)*LST_SZ_2_PROZENT + (LST_SZ_3-LST_SZ_2-LST_SZ_1-LST_SZ_FREI)*LST_SZ_3_PROZENT
                    restSB_lstbmg = 0.0
                    restSB_pr = 0.0
                    lst_bmg = lst_bmg + (rest_altsonder_sv - LST_SZ_3)
                
                if (altesonder+sonderzahlungen)<jahressechstel:
                    if restSB_pr == 0.0:
                        lst_bmg = lst_bmg + sonderzahlungen
                    elif restSB_pr == LST_SZ_1_PROZENT:
                        if restSB_lstbmg >= sonderzahlungen:
                            lst_sb = sonderzahlungen*LST_SZ_1_PROZENT
                        else:
                            lst_sb = restSB_lstbmg*LST_SZ_1_PROZENT + (sonderzahlungen-restSB_lstbmg)*LST_SZ_2_PROZENT
                    elif restSB_pr == LST_SZ_2_PROZENT:
                        if restSB_lstbmg >= sonderzahlungen:
                            lst_sb = sonderzahlungen*LST_SZ_2_PROZENT
                        else:
                            lst_sb = restSB_lstbmg*LST_SZ_2_PROZENT + (sonderzahlungen-restSB_lstbmg)*LST_SZ_3_PROZENT
                    elif restSB_pr == LST_SZ_3_PROZENT:
                        if restSB_lstbmg >= sonderzahlungen:
                            lst_sb = sonderzahlungen*LST_SZ_3_PROZENT
                        else:
                            lst_sb = restSB_lstbmg*LST_SZ_3_PROZENT
                            lst_bmg = lst_bmg + (sonderzahlungen-restSB_lstbmg)
                else:

                    offjahressechstel = jahressechstel - altesonder
                    sv_sb_teil1 = offjahressechstel*prsvsonder
                    sv_sb_teil2 = svsonder - sv_sb_teil1   
                    lst_bmg_sz = offjahressechstel - sv_sb_teil1
                    lst_bmg = lst_bmg + (sonderzahlungen - offjahressechstel) - sv_sb_teil2
                    #lst_bmg = lst_bmg + (altesonder-jahressechstel)                                             
                    if restSB_pr == 0.0:
                        lst_bmg = lst_bmg + lst_bmg_sz
                    elif restSB_pr == LST_SZ_1_PROZENT:
                        if restSB_lstbmg >= lst_bmg_sz:
                            lst_sb = lst_bmg_sz*LST_SZ_1_PROZENT
                        else:
                            lst_sb = restSB_lstbmg*LST_SZ_1_PROZENT + (lst_bmg_sz-restSB_lstbmg)*LST_SZ_2_PROZENT
                    elif restSB_pr == LST_SZ_2_PROZENT:
                        if restSB_lstbmg >= lst_bmg_sz:
                            lst_sb = lst_bmg_sz*LST_SZ_2_PROZENT
                        else:
                            lst_sb = restSB_lstbmg*LST_SZ_2_PROZENT + (lst_bmg_sz-restSB_lstbmg)*LST_SZ_3_PROZENT
                    elif restSB_pr == LST_SZ_3_PROZENT:
                        if restSB_lstbmg >= lst_bmg_sz:
                            lst_sb = lst_bmg_sz*LST_SZ_3_PROZENT
                        else:
                            lst_sb = restSB_lstbmg*LST_SZ_3_PROZENT
                            lst_bmg = lst_bmg + (lst_bmg_sz-restSB_lstbmg)

            else:

                sv_sb_teil1 = jahressechstel * prsvsonder
                sv_sb_teil2 = altesonder*prsvsonder - sv_sb_teil1
                lst_bmg_sz = jahressechstel - sv_sb_teil1
                lst_bmg = lst_bmg + (altesonder - jahressechstel) - sv_sb_teil2
                rest_altsonder_sv = jahressechstel - sv_sb_teil1

                rest_altsonder_sv = max(rest_altsonder_sv - LST_SZ_FREI, 0.0)

                if rest_altsonder_sv < LST_SZ_1:
                    
                    altsonder_sv = rest_altsonder_sv*LST_SZ_1_PROZENT
                    restSB_pr = LST_SZ_1_PROZENT
                    restSB_lstbmg = LST_SZ_1 - rest_altsonder_sv

                elif rest_altsonder_sv < LST_SZ_2:

                    altsonder_sv = LST_SZ_1*LST_SZ_1_PROZENT + (rest_altsonder_sv-LST_SZ_1)*LST_SZ_2_PROZENT
                    restSB_pr = LST_SZ_2_PROZENT
                    restSB_lstbmg = LST_SZ_2 - rest_altsonder_sv

                elif rest_altsonder_sv < (LST_SZ_3-LST_SZ_FREI):

                    altsonder_sv = LST_SZ_1*LST_SZ_1_PROZENT + (LST_SZ_2-LST_SZ_1)*LST_SZ_2_PROZENT + (rest_altsonder_sv-LST_SZ_2)*LST_SZ_3_PROZENT
                    restSB_pr = LST_SZ_3_PROZENT
                    restSB_lstbmg = (LST_SZ_3-LST_SZ_FREI) - rest_altsonder_sv

                else:

                    altsonder_sv = LST_SZ_1*LST_SZ_1_PROZENT + (LST_SZ_2-LST_SZ_1)*LST_SZ_2_PROZENT + (LST_SZ_3-LST_SZ_2-LST_SZ_1-LST_SZ_FREI)*LST_SZ_3_PROZENT
                    restSB_lstbmg = 0.0
                    restSB_pr = 0.0
                    lst_bmg = lst_bmg + (rest_altsonder_sv - LST_SZ_3)
                
                if restSB_pr == 0.0:
                    lst_bmg = lst_bmg + sonderzahlungen
                elif restSB_pr == LST_SZ_1_PROZENT:
                    if restSB_lstbmg >= sonderzahlungen:
                        lst_sb = sonderzahlungen*LST_SZ_1_PROZENT
                    else:
                        lst_sb = restSB_lstbmg*LST_SZ_1_PROZENT + (sonderzahlungen-restSB_lstbmg)*LST_SZ_2_PROZENT
                elif restSB_pr == LST_SZ_2_PROZENT:
                    if restSB_lstbmg >= sonderzahlungen:
                        lst_sb = sonderzahlungen*LST_SZ_2_PROZENT
                    else:
                        lst_sb = restSB_lstbmg*LST_SZ_2_PROZENT + (sonderzahlungen-restSB_lstbmg)*LST_SZ_3_PROZENT
                elif restSB_pr == LST_SZ_3_PROZENT:
                    if restSB_lstbmg >= sonderzahlungen:
                        lst_sb = sonderzahlungen*LST_SZ_3_PROZENT
                    else:
                        lst_sb = restSB_lstbmg*LST_SZ_3_PROZENT
                        lst_bmg = lst_bmg + (sonderzahlungen-restSB_lstbmg) 

        else:
                    
            if jahressechstel > sonderzahlungen:
                lst_bmg_sz = sonderzahlungen - svsonder
                
                lst_bmg_sz = lst_bmg_sz - 620.

                if lst_bmg_sz < LST_SZ_1:
                    lst_sb = lst_bmg_sz*LST_SZ_1_PROZENT
                else:
                    if lst_bmg_sz < LST_SZ_2:
                        lst_sb = LST_SZ_1*LST_SZ_1_PROZENT + (lst_bmg_sz-LST_SZ_1)*LST_SZ_2_PROZENT
                    else:
                        if lst_bmg_sz < LST_SZ_3:
                            lst_sb = LST_SZ_1*LST_SZ_1_PROZENT + (LST_SZ_2-LST_SZ_1)*LST_SZ_2_PROZENT + (lst_bmg_sz-LST_SZ_2)*LST_SZ_3_PROZENT
                        else:
                            lst_sb = LST_SZ_1*LST_SZ_1_PROZENT + (LST_SZ_2-LST_SZ_1)*LST_SZ_2_PROZENT + (LST_SZ_3-LST_SZ_2-LST_SZ_1-LST_SZ_FREI)*LST_SZ_3_PROZENT
                            lst_bmg = lst_bmg + (lst_bmg_sz - LST_SZ_3)
            else:

                sv_sb_teil1 = jahressechstel * prsvsonder
                sv_sb_teil2 = svsonder - sv_sb_teil1
                lst_bmg_sz = jahressechstel - sv_sb_teil1
                lst_bmg = lst_bmg + (sonderzahlungen - jahressechstel) - sv_sb_teil2
                
                lst_bmg_sz = lst_bmg_sz - LST_SZ_FREI

                if lst_bmg_sz < LST_SZ_1:
                    lst_sb = lst_bmg_sz*LST_SZ_1_PROZENT
                else:
                    if lst_bmg_sz < LST_SZ_2:
                        lst_sb = LST_SZ_1*LST_SZ_1_PROZENT + (lst_bmg_sz-LST_SZ_1)*LST_SZ_2_PROZENT
                    else:
                        if lst_bmg_sz < LST_SZ_3:
                            lst_sb = LST_SZ_1*LST_SZ_1_PROZENT + (LST_SZ_2-LST_SZ_1)*LST_SZ_2_PROZENT + (lst_bmg_sz-LST_SZ_2)*LST_SZ_3_PROZENT
                        else:
                            lst_sb = LST_SZ_1*LST_SZ_1_PROZENT + (LST_SZ_2-LST_SZ_1)*LST_SZ_2_PROZENT + (LST_SZ_3-LST_SZ_2-LST_SZ_1-LST_SZ_FREI)*LST_SZ_3_PROZENT
                            lst_bmg = lst_bmg + (lst_bmg_sz - LST_SZ_3)

    else:
        lst_sb = 0.

    if lst_bmg < LST_ST1:
        lst = lst_bmg*LST_ST1_PROZENT
    elif lst_bmg < LST_ST2:
        lst = lst_bmg*LST_ST2_PROZENT - LST_ST2_ABZUG - LST_VAB
    elif lst_bmg < LST_ST3:
        lst = lst_bmg*LST_ST3_PROZENT - LST_ST3_ABZUG - LST_VAB
    elif lst_bmg < LST_ST4:
        lst = lst_bmg*LST_ST4_PROZENT - LST_ST4_ABZUG - LST_VAB
    elif lst_bmg < LST_ST5:
        lst = lst_bmg*LST_ST5_PROZENT - LST_ST5_ABZUG - LST_VAB
    elif lst_bmg < LST_ST6:
        lst = lst_bmg*LST_ST6_PROZENT - LST_ST6_ABZUG - LST_VAB
    else:
        lst = lst_bmg*LST_ST7_PROZENT - LST_ST7_ABZUG - LST_VAB

    lst = max(lst - FaBoP, 0.0) - pendlereuro - av
    netto = brlohn - sv - lst
    sobz = sonderzahlungen - svsonder - lst_sb

    string2print = (
        f"\n{RED}{BOLD}================================================================================{RESET}\n"
        f"{BOLD}  Der Nettolohn lt Berechnung (2021) ist:{RESET} {GREEN}{BOLD}{netto}€{RESET}\n"
        f"{RED}{BOLD}================================================================================{RESET}\n\n"
        f"SV_Bmg: {sv_bmg}€    SV lfd: {sv}€\n"
        f"Lst_Bmg: {lst_bmg}€   Lohnsteuer: {lst}€\n\n"
        f"Der sonstige Bezug (netto) ist: {sobz}\n"
        f"SV-Sonstiger Bezug: {svsonder}€   Lohnsteuer-Sonstiger Bezug: {lst_sb}€\n\n"
        f"Lohnnebenkosten\n"
        f"Kommunlasteuer: {kommst}€   U-bahnsteuer: {dga}€   Dienstbeitrag: {db}€   "
        f"Zuschlag (DB): {dz}€   SV-Dienstgeberbeitrag: {(dienstg_sv + dienstg_svsonder)}€   BV: {BV}€"
    )

    string2print_farblos = (
    f"\n================================================================================\n"
    f"  Der Nettolohn lt Berechnung (2021) ist: {netto}€\n"
    f"================================================================================\n\n"
    f"SV_Bmg: {sv_bmg}€    SV lfd: {sv}€\n"
    f"Lst_Bmg: {lst_bmg}€   Lohnsteuer: {lst}€\n\n"
    f"Der sonstige Bezug (netto) ist: {sobz}€\n"
    f"SV-Sonstiger Bezug: {svsonder}€   Lohnsteuer-Sonstiger Bezug: {lst_sb}€\n\n"
    f"Lohnnebenkosten\n"
    f"Kommunalsteuer: {kommst}€   U-Bahnsteuer: {dga}€   Dienstbeitrag: {db}€   "
    f"Zuschlag (DB): {dz}€   SV-Dienstgeberbeitrag: {(dienstg_sv + dienstg_svsonder)}€   BV: {BV}€"
)


    return string2print_farblos


if __name__ == "__main__":
    # Test the function

    monat = int(input("Gib den Monat als Zahl an:\n"))
    jahr = int(input("Gib das Jahr als Zahl an:\n"))
    stundensatz = float(input("Gib die Arbeitsstunden/Woche an:\n"))
    brutto = float(input("Gib Bruttolohn ein:\n"))

    # mehr0 = float(input("Gib Mehrstunden mit 0% ein:\n"))
    # mehr25 = float(input("Gib Mehrstunden mit 25% ein:\n"))
    # mehr50 = float(input("Gib Mehrstunden mit 50% ein:\n"))
    # überst50 = float(input("Gib Überstunden mit 50% ein:\n"))
    # überst100 = float(input("Gib Überstunden mit 100% ein:\n"))

    # sonderz = float(input("Gib Sonderzahlung ein:\n"))
    # sachbez = float(input("Gib Sachbezug ein:\n"))
    # diäten = float(input("Gib Diäten (km-, Verpflegungsgeld) ein:\n"))
    # reisek = float(input("Gib die Reisekosten (Tag- und Nachtgeld) ein:\n"))

    # fbb = float(input("Gib den Freibetragsbescheid an:\n"))
    # PP = float(input("Gib die Pendlerpauschale an:\n"))
    # PEur = float(input("Gib den Pendlereuro ein:\n"))
    # AV_str = int(input("Besteht AlleinVerdiener-/AlleinErzieheranspruch? (Anzahl der Kinder)\n"))
    # FaBoP = True if input("Besteht Anspruch auf den Familienbonus? (y/n)\n").upper() == "Y" else False
    # ÖGB = True if input("Ist der Arbeiter/Angestellte Gewerkschaftsmitglied? (y/n):\n").upper() == "Y" else False

    # jahressechstel = float(input("Gib das aktuelle Jahressechstel (J/6) an:\n"))

    calc_brutto2netto(
        monat=monat,
        jahr=jahr,
        stundensatz=stundensatz,
        brutto=brutto,
        #  mehrstunden0=mehr0,
        # mehrstunden25=mehr25,
        # mehrstunden50=mehr50,
        # überstunden50=überst50,
        # überstunden100=überst100,
        # sonderzahlungen=sonderz,
        # sachbezug=sachbez,
        # diäten=diäten, reisekosten=reisek, 
        # freibetragsbescheid=fbb, 
        # pendlerpauschale=PP, pendlereuro=PEur, 
        # anzahl_Kinder_AVAB=AV_str, 
        # anspruch_fabo=FaBoP, 
        # gewerkschaftmitglied=ÖGB
                      )
    input("Zum Beenden beliebige Taste drücken!")
