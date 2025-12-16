"""All enum classes, including stage properties, connection properties, and fields."""

from enum import Enum


class SPLIT_VECTOR:
    """Enums for properties in the SPLIT_VECTOR stage."""

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class DIFFERENCE:
    """Enums for properties in the DIFFERENCE stage."""

    class AllValues(Enum):
        """Enum for the AllValues property."""

        false = " "
        true = "allValues"

    class CiCs2(Enum):
        """Enum for the CiCs2 property."""

        ci = "ci"
        cs = "cs"

    class Stats(Enum):
        """Enum for the Stats property."""

        false = " "
        true = "stats"

    class DropInsert(Enum):
        """Enum for the DropInsert property."""

        false = " "
        true = "dropInsert"

    class DropDelete(Enum):
        """Enum for the DropDelete property."""

        false = " "
        true = "dropDelete"

    class DropEdit(Enum):
        """Enum for the DropEdit property."""

        false = " "
        true = "dropEdit"

    class DropCopy(Enum):
        """Enum for the DropCopy property."""

        false = " "
        true = "dropCopy"

    class TolerateUnsorted(Enum):
        """Enum for the TolerateUnsorted property."""

        false = " "
        true = "tolerateUnsorted"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ValueCiCs(Enum):
        """Enum for the ValueCiCs property."""

        ci = "ci"
        cs = "cs"

    class CollationSequence(Enum):
        """Enum for the CollationSequence property."""

        OFF = "OFF"
        af = "af"
        af_NA = "af_NA"
        af_ZA = "af_ZA"
        agq = "agq"
        agq_CM = "agq_CM"
        ak = "ak"
        ak_GH = "ak_GH"
        am = "am"
        am_ET = "am_ET"
        ar = "ar"
        ar_001 = "ar_001"
        ar_AE = "ar_AE"
        ar_BH = "ar_BH"
        ar_DJ = "ar_DJ"
        ar_DZ = "ar_DZ"
        ar_EG = "ar_EG"
        ar_EH = "ar_EH"
        ar_ER = "ar_ER"
        ar_IL = "ar_IL"
        ar_IQ = "ar_IQ"
        ar_JO = "ar_JO"
        ar_KM = "ar_KM"
        ar_KW = "ar_KW"
        ar_LB = "ar_LB"
        ar_LY = "ar_LY"
        ar_MA = "ar_MA"
        ar_MR = "ar_MR"
        ar_OM = "ar_OM"
        ar_PS = "ar_PS"
        ar_QA = "ar_QA"
        ar_SA = "ar_SA"
        ar_SD = "ar_SD"
        ar_SO = "ar_SO"
        ar_SY = "ar_SY"
        ar_TD = "ar_TD"
        ar_TN = "ar_TN"
        ar_YE = "ar_YE"
        as_ = "as"
        as_IN = "as_IN"
        asa = "asa"
        asa_TZ = "asa_TZ"
        az = "az"
        az_Cyrl = "az_Cyrl"
        az_Cyrl_AZ = "az_Cyrl_AZ"
        az_Latn = "az_Latn"
        az_Latn_AZ = "az_Latn_AZ"
        bas = "bas"
        bas_CM = "bas_CM"
        be = "be"
        be_BY = "be_BY"
        bem = "bem"
        bem_ZM = "bem_ZM"
        bez = "bez"
        bez_TZ = "bez_TZ"
        bg = "bg"
        bg_BG = "bg_BG"
        bm = "bm"
        bm_ML = "bm_ML"
        bn = "bn"
        bn_BD = "bn_BD"
        bn_IN = "bn_IN"
        bo = "bo"
        bo_CN = "bo_CN"
        bo_IN = "bo_IN"
        br = "br"
        br_FR = "br_FR"
        brx = "brx"
        brx_IN = "brx_IN"
        bs = "bs"
        bs_Cyrl = "bs_Cyrl"
        bs_Cyrl_BA = "bs_Cyrl_BA"
        bs_Latn = "bs_Latn"
        bs_Latn_BA = "bs_Latn_BA"
        ca = "ca"
        ca_AD = "ca_AD"
        ca_ES = "ca_ES"
        cgg = "cgg"
        cgg_UG = "cgg_UG"
        chr = "chr"
        chr_US = "chr_US"
        cs = "cs"
        cs_CZ = "cs_CZ"
        cy = "cy"
        cy_GB = "cy_GB"
        da = "da"
        da_DK = "da_DK"
        dav = "dav"
        dav_KE = "dav_KE"
        de = "de"
        de_AT = "de_AT"
        de_BE = "de_BE"
        de_CH = "de_CH"
        de_DE = "de_DE"
        de_LI = "de_LI"
        de_LU = "de_LU"
        dje = "dje"
        dje_NE = "dje_NE"
        dua = "dua"
        dua_CM = "dua_CM"
        dyo = "dyo"
        dyo_SN = "dyo_SN"
        dz = "dz"
        dz_BT = "dz_BT"
        ebu = "ebu"
        ebu_KE = "ebu_KE"
        ee = "ee"
        ee_GH = "ee_GH"
        ee_TG = "ee_TG"
        el = "el"
        el_CY = "el_CY"
        el_GR = "el_GR"
        en = "en"
        en_150 = "en_150"
        en_AG = "en_AG"
        en_AS = "en_AS"
        en_AU = "en_AU"
        en_BB = "en_BB"
        en_BE = "en_BE"
        en_BM = "en_BM"
        en_BS = "en_BS"
        en_BW = "en_BW"
        en_BZ = "en_BZ"
        en_CA = "en_CA"
        en_CM = "en_CM"
        en_DM = "en_DM"
        en_FJ = "en_FJ"
        en_FM = "en_FM"
        en_GB = "en_GB"
        en_GD = "en_GD"
        en_GG = "en_GG"
        en_GH = "en_GH"
        en_GI = "en_GI"
        en_GM = "en_GM"
        en_GU = "en_GU"
        en_GY = "en_GY"
        en_HK = "en_HK"
        en_IE = "en_IE"
        en_IM = "en_IM"
        en_IN = "en_IN"
        en_JE = "en_JE"
        en_JM = "en_JM"
        en_KE = "en_KE"
        en_KI = "en_KI"
        en_KN = "en_KN"
        en_KY = "en_KY"
        en_LC = "en_LC"
        en_LR = "en_LR"
        en_LS = "en_LS"
        en_MG = "en_MG"
        en_MH = "en_MH"
        en_MP = "en_MP"
        en_MT = "en_MT"
        en_MU = "en_MU"
        en_MW = "en_MW"
        en_NA = "en_NA"
        en_NG = "en_NG"
        en_NZ = "en_NZ"
        en_PG = "en_PG"
        en_PH = "en_PH"
        en_PK = "en_PK"
        en_PR = "en_PR"
        en_PW = "en_PW"
        en_SB = "en_SB"
        en_SC = "en_SC"
        en_SG = "en_SG"
        en_SL = "en_SL"
        en_SS = "en_SS"
        en_SZ = "en_SZ"
        en_TC = "en_TC"
        en_TO = "en_TO"
        en_TT = "en_TT"
        en_TZ = "en_TZ"
        en_UG = "en_UG"
        en_UM = "en_UM"
        en_US = "en_US"
        en_US_POSIX = "en_US_POSIX"
        en_VC = "en_VC"
        en_VG = "en_VG"
        en_VI = "en_VI"
        en_VU = "en_VU"
        en_WS = "en_WS"
        en_ZA = "en_ZA"
        en_ZM = "en_ZM"
        en_ZW = "en_ZW"
        eo = "eo"
        es = "es"
        es_419 = "es_419"
        es_AR = "es_AR"
        es_BO = "es_BO"
        es_CL = "es_CL"
        es_CO = "es_CO"
        es_CR = "es_CR"
        es_CU = "es_CU"
        es_DO = "es_DO"
        es_EA = "es_EA"
        es_EC = "es_EC"
        es_ES = "es_ES"
        es_GQ = "es_GQ"
        es_GT = "es_GT"
        es_HN = "es_HN"
        es_IC = "es_IC"
        es_MX = "es_MX"
        es_NI = "es_NI"
        es_PA = "es_PA"
        es_PE = "es_PE"
        es_PH = "es_PH"
        es_PR = "es_PR"
        es_PY = "es_PY"
        es_SV = "es_SV"
        es_US = "es_US"
        es_UY = "es_UY"
        es_VE = "es_VE"
        et = "et"
        et_EE = "et_EE"
        eu = "eu"
        eu_ES = "eu_ES"
        ewo = "ewo"
        ewo_CM = "ewo_CM"
        fa = "fa"
        fa_AF = "fa_AF"
        fa_IR = "fa_IR"
        ff = "ff"
        ff_SN = "ff_SN"
        fi = "fi"
        fi_FI = "fi_FI"
        fil = "fil"
        fil_PH = "fil_PH"
        fo = "fo"
        fo_FO = "fo_FO"
        fr = "fr"
        fr_BE = "fr_BE"
        fr_BF = "fr_BF"
        fr_BI = "fr_BI"
        fr_BJ = "fr_BJ"
        fr_BL = "fr_BL"
        fr_CA = "fr_CA"
        fr_CD = "fr_CD"
        fr_CF = "fr_CF"
        fr_CG = "fr_CG"
        fr_CH = "fr_CH"
        fr_CI = "fr_CI"
        fr_CM = "fr_CM"
        fr_DJ = "fr_DJ"
        fr_DZ = "fr_DZ"
        fr_FR = "fr_FR"
        fr_GA = "fr_GA"
        fr_GF = "fr_GF"
        fr_GN = "fr_GN"
        fr_GP = "fr_GP"
        fr_GQ = "fr_GQ"
        fr_HT = "fr_HT"
        fr_KM = "fr_KM"
        fr_LU = "fr_LU"
        fr_MA = "fr_MA"
        fr_MC = "fr_MC"
        fr_MF = "fr_MF"
        fr_MG = "fr_MG"
        fr_ML = "fr_ML"
        fr_MQ = "fr_MQ"
        fr_MR = "fr_MR"
        fr_MU = "fr_MU"
        fr_NC = "fr_NC"
        fr_NE = "fr_NE"
        fr_PF = "fr_PF"
        fr_RE = "fr_RE"
        fr_RW = "fr_RW"
        fr_SC = "fr_SC"
        fr_SN = "fr_SN"
        fr_SY = "fr_SY"
        fr_TD = "fr_TD"
        fr_TG = "fr_TG"
        fr_TN = "fr_TN"
        fr_VU = "fr_VU"
        fr_YT = "fr_YT"
        ga = "ga"
        ga_IE = "ga_IE"
        gl = "gl"
        gl_ES = "gl_ES"
        gsw = "gsw"
        gsw_CH = "gsw_CH"
        gu = "gu"
        gu_IN = "gu_IN"
        guz = "guz"
        guz_KE = "guz_KE"
        gv = "gv"
        gv_GB = "gv_GB"
        ha = "ha"
        ha_Latn = "ha_Latn"
        ha_Latn_GH = "ha_Latn_GH"
        ha_Latn_NE = "ha_Latn_NE"
        ha_Latn_NG = "ha_Latn_NG"
        haw = "haw"
        haw_US = "haw_US"
        he = "he"
        he_IL = "he_IL"
        hi = "hi"
        hi_IN = "hi_IN"
        hr = "hr"
        hr_BA = "hr_BA"
        hr_HR = "hr_HR"
        hu = "hu"
        hu_HU = "hu_HU"
        hy = "hy"
        hy_AM = "hy_AM"
        id = "id"
        id_ID = "id_ID"
        ig = "ig"
        ig_NG = "ig_NG"
        ii = "ii"
        ii_CN = "ii_CN"
        is_ = "is"
        is_IS = "is_IS"
        it = "it"
        it_CH = "it_CH"
        it_IT = "it_IT"
        it_SM = "it_SM"
        ja = "ja"
        ja_JP = "ja_JP"
        jgo = "jgo"
        jgo_CM = "jgo_CM"
        jmc = "jmc"
        jmc_TZ = "jmc_TZ"
        ka = "ka"
        ka_GE = "ka_GE"
        kab = "kab"
        kab_DZ = "kab_DZ"
        kam = "kam"
        kam_KE = "kam_KE"
        kde = "kde"
        kde_TZ = "kde_TZ"
        kea = "kea"
        kea_CV = "kea_CV"
        khq = "khq"
        khq_ML = "khq_ML"
        ki = "ki"
        ki_KE = "ki_KE"
        kk = "kk"
        kk_Cyrl = "kk_Cyrl"
        kk_Cyrl_KZ = "kk_Cyrl_KZ"
        kl = "kl"
        kl_GL = "kl_GL"
        kln = "kln"
        kln_KE = "kln_KE"
        km = "km"
        km_KH = "km_KH"
        kn = "kn"
        kn_IN = "kn_IN"
        ko = "ko"
        ko_KP = "ko_KP"
        ko_KR = "ko_KR"
        kok = "kok"
        kok_IN = "kok_IN"
        ks = "ks"
        ks_Arab = "ks_Arab"
        ks_Arab_IN = "ks_Arab_IN"
        ksb = "ksb"
        ksb_TZ = "ksb_TZ"
        ksf = "ksf"
        ksf_CM = "ksf_CM"
        kw = "kw"
        kw_GB = "kw_GB"
        lag = "lag"
        lag_TZ = "lag_TZ"
        lg = "lg"
        lg_UG = "lg_UG"
        ln = "ln"
        ln_AO = "ln_AO"
        ln_CD = "ln_CD"
        ln_CF = "ln_CF"
        ln_CG = "ln_CG"
        lo = "lo"
        lo_LA = "lo_LA"
        lt = "lt"
        lt_LT = "lt_LT"
        lu = "lu"
        lu_CD = "lu_CD"
        luo = "luo"
        luo_KE = "luo_KE"
        luy = "luy"
        luy_KE = "luy_KE"
        lv = "lv"
        lv_LV = "lv_LV"
        mas = "mas"
        mas_KE = "mas_KE"
        mas_TZ = "mas_TZ"
        mer = "mer"
        mer_KE = "mer_KE"
        mfe = "mfe"
        mfe_MU = "mfe_MU"
        mg = "mg"
        mg_MG = "mg_MG"
        mgh = "mgh"
        mgh_MZ = "mgh_MZ"
        mgo = "mgo"
        mgo_CM = "mgo_CM"
        mk = "mk"
        mk_MK = "mk_MK"
        ml = "ml"
        ml_IN = "ml_IN"
        mr = "mr"
        mr_IN = "mr_IN"
        ms = "ms"
        ms_BN = "ms_BN"
        ms_MY = "ms_MY"
        ms_SG = "ms_SG"
        mt = "mt"
        mt_MT = "mt_MT"
        mua = "mua"
        mua_CM = "mua_CM"
        my = "my"
        my_MM = "my_MM"
        naq = "naq"
        naq_NA = "naq_NA"
        nb = "nb"
        nb_NO = "nb_NO"
        nd = "nd"
        nd_ZW = "nd_ZW"
        ne = "ne"
        ne_IN = "ne_IN"
        ne_NP = "ne_NP"
        nl = "nl"
        nl_AW = "nl_AW"
        nl_BE = "nl_BE"
        nl_CW = "nl_CW"
        nl_NL = "nl_NL"
        nl_SR = "nl_SR"
        nl_SX = "nl_SX"
        nmg = "nmg"
        nmg_CM = "nmg_CM"
        nn = "nn"
        nn_NO = "nn_NO"
        nus = "nus"
        nus_SD = "nus_SD"
        nyn = "nyn"
        nyn_UG = "nyn_UG"
        om = "om"
        om_ET = "om_ET"
        om_KE = "om_KE"
        or_ = "or"
        or_IN = "or_IN"
        pa = "pa"
        pa_Arab = "pa_Arab"
        pa_Arab_PK = "pa_Arab_PK"
        pa_Guru = "pa_Guru"
        pa_Guru_IN = "pa_Guru_IN"
        pl = "pl"
        pl_PL = "pl_PL"
        ps = "ps"
        ps_AF = "ps_AF"
        pt = "pt"
        pt_AO = "pt_AO"
        pt_BR = "pt_BR"
        pt_CV = "pt_CV"
        pt_GW = "pt_GW"
        pt_MO = "pt_MO"
        pt_MZ = "pt_MZ"
        pt_PT = "pt_PT"
        pt_ST = "pt_ST"
        pt_TL = "pt_TL"
        rm = "rm"
        rm_CH = "rm_CH"
        rn = "rn"
        rn_BI = "rn_BI"
        ro = "ro"
        ro_MD = "ro_MD"
        ro_RO = "ro_RO"
        rof = "rof"
        rof_TZ = "rof_TZ"
        ru = "ru"
        ru_BY = "ru_BY"
        ru_KG = "ru_KG"
        ru_KZ = "ru_KZ"
        ru_MD = "ru_MD"
        ru_RU = "ru_RU"
        ru_UA = "ru_UA"
        rw = "rw"
        rw_RW = "rw_RW"
        rwk = "rwk"
        rwk_TZ = "rwk_TZ"
        saq = "saq"
        saq_KE = "saq_KE"
        sbp = "sbp"
        sbp_TZ = "sbp_TZ"
        seh = "seh"
        seh_MZ = "seh_MZ"
        ses = "ses"
        ses_ML = "ses_ML"
        sg = "sg"
        sg_CF = "sg_CF"
        shi = "shi"
        shi_Latn = "shi_Latn"
        shi_Latn_MA = "shi_Latn_MA"
        shi_Tfng = "shi_Tfng"
        shi_Tfng_MA = "shi_Tfng_MA"
        si = "si"
        si_LK = "si_LK"
        sk = "sk"
        sk_SK = "sk_SK"
        sl = "sl"
        sl_SI = "sl_SI"
        sn = "sn"
        sn_ZW = "sn_ZW"
        so = "so"
        so_DJ = "so_DJ"
        so_ET = "so_ET"
        so_KE = "so_KE"
        so_SO = "so_SO"
        sq = "sq"
        sq_AL = "sq_AL"
        sq_MK = "sq_MK"
        sr = "sr"
        sr_Cyrl = "sr_Cyrl"
        sr_Cyrl_BA = "sr_Cyrl_BA"
        sr_Cyrl_ME = "sr_Cyrl_ME"
        sr_Cyrl_RS = "sr_Cyrl_RS"
        sr_Latn = "sr_Latn"
        sr_Latn_BA = "sr_Latn_BA"
        sr_Latn_ME = "sr_Latn_ME"
        sr_Latn_RS = "sr_Latn_RS"
        sv = "sv"
        sv_AX = "sv_AX"
        sv_FI = "sv_FI"
        sv_SE = "sv_SE"
        sw = "sw"
        sw_KE = "sw_KE"
        sw_TZ = "sw_TZ"
        sw_UG = "sw_UG"
        swc = "swc"
        swc_CD = "swc_CD"
        ta = "ta"
        ta_IN = "ta_IN"
        ta_LK = "ta_LK"
        ta_MY = "ta_MY"
        ta_SG = "ta_SG"
        te = "te"
        te_IN = "te_IN"
        teo = "teo"
        teo_KE = "teo_KE"
        teo_UG = "teo_UG"
        th = "th"
        th_TH = "th_TH"
        ti = "ti"
        ti_ER = "ti_ER"
        ti_ET = "ti_ET"
        to = "to"
        to_TO = "to_TO"
        tr = "tr"
        tr_CY = "tr_CY"
        tr_TR = "tr_TR"
        twq = "twq"
        twq_NE = "twq_NE"
        tzm = "tzm"
        tzm_Latn = "tzm_Latn"
        tzm_Latn_MA = "tzm_Latn_MA"
        uk = "uk"
        uk_UA = "uk_UA"
        ur = "ur"
        ur_IN = "ur_IN"
        ur_PK = "ur_PK"
        uz = "uz"
        uz_Arab = "uz_Arab"
        uz_Arab_AF = "uz_Arab_AF"
        uz_Cyrl = "uz_Cyrl"
        uz_Cyrl_UZ = "uz_Cyrl_UZ"
        uz_Latn = "uz_Latn"
        uz_Latn_UZ = "uz_Latn_UZ"
        vai = "vai"
        vai_Latn = "vai_Latn"
        vai_Latn_LR = "vai_Latn_LR"
        vai_Vaii = "vai_Vaii"
        vai_Vaii_LR = "vai_Vaii_LR"
        vi = "vi"
        vi_VN = "vi_VN"
        vun = "vun"
        vun_TZ = "vun_TZ"
        xog = "xog"
        xog_UG = "xog_UG"
        yav = "yav"
        yav_CM = "yav_CM"
        yo = "yo"
        yo_NG = "yo_NG"
        zh = "zh"
        zh_Hans = "zh_Hans"
        zh_Hans_CN = "zh_Hans_CN"
        zh_Hans_HK = "zh_Hans_HK"
        zh_Hans_MO = "zh_Hans_MO"
        zh_Hans_SG = "zh_Hans_SG"
        zh_Hant = "zh_Hant"
        zh_Hant_HK = "zh_Hant_HK"
        zh_Hant_MO = "zh_Hant_MO"
        zh_Hant_TW = "zh_Hant_TW"
        zu = "zu"
        zu_ZA = "zu_ZA"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class DECODE:
    """Enums for properties in the DECODE stage."""

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class SURVIVE:
    """Enums for properties in the SURVIVE stage."""

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class Db2NameSelect(Enum):
        """Enum for the Db2NameSelect property."""

        use_db2NameEnv = "use_db2NameEnv"
        use_userDefinedName = "use_userDefinedName"

    class Db2InstanceSelect(Enum):
        """Enum for the Db2InstanceSelect property."""

        use_db2InstanceEnv = "use_db2InstanceEnv"
        use_userDefinedInstance = "use_userDefinedInstance"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class SAMPLE:
    """Enums for properties in the SAMPLE stage."""

    class Selection(Enum):
        """Enum for the Selection property."""

        percent = "percent"
        period = "period"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class ADDRESS_VERIFICATION:
    """Enums for properties in the ADDRESS_VERIFICATION stage."""

    class ProcessingType(Enum):
        """Enum for the ProcessingType property."""

        Parse = "Parse"
        Validation = "Validation"

    class EnableFieldStatus(Enum):
        """Enum for the EnableFieldStatus property."""

        No = "No"
        Yes = "Yes"

    class EnableFieldMatchScore(Enum):
        """Enum for the EnableFieldMatchScore property."""

        No = "No"
        Yes = "Yes"

    class AddressLineSeparator(Enum):
        """Enum for the AddressLineSeparator property."""

        PIPE = "PIPE"
        COMMA = "COMMA"
        CRLF = "CRLF"
        CR = "CR"
        LF = "LF"
        SEMICOLON = "SEMICOLON"
        SPACE = "SPACE"
        TAB = "TAB"

    class MinimumVerificationLevel(Enum):
        """Enum for the MinimumVerificationLevel property."""

        none = "0"
        administrative_area = "1"
        locality = "2"
        thoroughfare = "3"
        premise_or_building = "4"
        delivery_point_post_offic_box_subbuilding = "5"

    class OutputCasing(Enum):
        """Enum for the OutputCasing property."""

        Title = "Title"
        Upper = "Upper"
        Lower = "Lower"

    class OutputScript(Enum):
        """Enum for the OutputScript property."""

        AsProcessed = "AsProcessed"
        Native = "Native"
        Latn = "Latn"

    class UseSymbolicTransliteration(Enum):
        """Enum for the UseSymbolicTransliteration property."""

        false = "False"
        true = "True"

    class UseCityAbbreviations(Enum):
        """Enum for the UseCityAbbreviations property."""

        Yes = "Yes"
        No = "No"

    class LessUsedFields(Enum):
        """Enum for the LessUsedFields property."""

        No = "No"
        Yes = "Yes"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ValidationType(Enum):
        """Enum for the ValidationType property."""

        CorrectionOnly = "CorrectionOnly"
        Suggestion = "Suggestion"
        ReverseGeocode = "ReverseGeocode"
        USPSCertification = "USPSCertification"

    class GeoCoding(Enum):
        """Enum for the GeoCoding property."""

        No = "No"
        Yes = "Yes"

    class EnhancedUS(Enum):
        """Enum for the EnhancedUS property."""

        No = "No"
        Yes = "Yes"

    class EnhancedGB(Enum):
        """Enum for the EnhancedGB property."""

        No = "No"
        Yes = "Yes"

    class Error(Enum):
        """Enum for the Error property."""

        No = "No"
        Yes = "Yes"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class Db2NameSelect(Enum):
        """Enum for the Db2NameSelect property."""

        use_db2NameEnv = "use_db2NameEnv"
        use_userDefinedName = "use_userDefinedName"

    class Db2InstanceSelect(Enum):
        """Enum for the Db2InstanceSelect property."""

        use_db2InstanceEnv = "use_db2InstanceEnv"
        use_userDefinedInstance = "use_userDefinedInstance"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        Select_a_column = "Select a column"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class MATCH_FREQUENCY:
    """Enums for properties in the MATCH_FREQUENCY stage."""

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class Pgmtype(Enum):
        """Enum for the Pgmtype property."""

        one_to_one = "one_to_one"
        dependent = "dependent"

    class Abtype(Enum):
        """Enum for the Abtype property."""

        Data = "Data"
        Reference = "Reference"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class Db2NameSelect(Enum):
        """Enum for the Db2NameSelect property."""

        use_db2NameEnv = "use_db2NameEnv"
        use_userDefinedName = "use_userDefinedName"

    class Db2InstanceSelect(Enum):
        """Enum for the Db2InstanceSelect property."""

        use_db2InstanceEnv = "use_db2InstanceEnv"
        use_userDefinedInstance = "use_userDefinedInstance"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        Select_a_column = "Select a column"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class ONE_SOURCE_MATCH:
    """Enums for properties in the ONE_SOURCE_MATCH stage."""

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class Pgmtype(Enum):
        """Enum for the Pgmtype property."""

        dependent = "Dependent"
        independent = "Independent"
        transitive = "Transitive"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class Db2NameSelect(Enum):
        """Enum for the Db2NameSelect property."""

        use_db2NameEnv = "use_db2NameEnv"
        use_userDefinedName = "use_userDefinedName"

    class Db2InstanceSelect(Enum):
        """Enum for the Db2InstanceSelect property."""

        use_db2InstanceEnv = "use_db2InstanceEnv"
        use_userDefinedInstance = "use_userDefinedInstance"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        Select_a_column = "Select a column"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class SWITCH:
    """Enums for properties in the SWITCH stage."""

    class Key(Enum):
        """Enum for the Key property."""

        custom = " "

    class Selection(Enum):
        """Enum for the Selection property."""

        auto = "auto"
        hash = "hash"
        user = "user"

    class CiCs(Enum):
        """Enum for the CiCs property."""

        cs = "cs"
        ci = "ci"

    class IfNotFound(Enum):
        """Enum for the IfNotFound property."""

        allow = "allow"
        ignore = "ignore"
        fail = "fail"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class CollationSequence(Enum):
        """Enum for the CollationSequence property."""

        OFF = "OFF"
        af = "af"
        af_NA = "af_NA"
        af_ZA = "af_ZA"
        agq = "agq"
        agq_CM = "agq_CM"
        ak = "ak"
        ak_GH = "ak_GH"
        am = "am"
        am_ET = "am_ET"
        ar = "ar"
        ar_001 = "ar_001"
        ar_AE = "ar_AE"
        ar_BH = "ar_BH"
        ar_DJ = "ar_DJ"
        ar_DZ = "ar_DZ"
        ar_EG = "ar_EG"
        ar_EH = "ar_EH"
        ar_ER = "ar_ER"
        ar_IL = "ar_IL"
        ar_IQ = "ar_IQ"
        ar_JO = "ar_JO"
        ar_KM = "ar_KM"
        ar_KW = "ar_KW"
        ar_LB = "ar_LB"
        ar_LY = "ar_LY"
        ar_MA = "ar_MA"
        ar_MR = "ar_MR"
        ar_OM = "ar_OM"
        ar_PS = "ar_PS"
        ar_QA = "ar_QA"
        ar_SA = "ar_SA"
        ar_SD = "ar_SD"
        ar_SO = "ar_SO"
        ar_SY = "ar_SY"
        ar_TD = "ar_TD"
        ar_TN = "ar_TN"
        ar_YE = "ar_YE"
        as_ = "as"
        as_IN = "as_IN"
        asa = "asa"
        asa_TZ = "asa_TZ"
        az = "az"
        az_Cyrl = "az_Cyrl"
        az_Cyrl_AZ = "az_Cyrl_AZ"
        az_Latn = "az_Latn"
        az_Latn_AZ = "az_Latn_AZ"
        bas = "bas"
        bas_CM = "bas_CM"
        be = "be"
        be_BY = "be_BY"
        bem = "bem"
        bem_ZM = "bem_ZM"
        bez = "bez"
        bez_TZ = "bez_TZ"
        bg = "bg"
        bg_BG = "bg_BG"
        bm = "bm"
        bm_ML = "bm_ML"
        bn = "bn"
        bn_BD = "bn_BD"
        bn_IN = "bn_IN"
        bo = "bo"
        bo_CN = "bo_CN"
        bo_IN = "bo_IN"
        br = "br"
        br_FR = "br_FR"
        brx = "brx"
        brx_IN = "brx_IN"
        bs = "bs"
        bs_Cyrl = "bs_Cyrl"
        bs_Cyrl_BA = "bs_Cyrl_BA"
        bs_Latn = "bs_Latn"
        bs_Latn_BA = "bs_Latn_BA"
        ca = "ca"
        ca_AD = "ca_AD"
        ca_ES = "ca_ES"
        cgg = "cgg"
        cgg_UG = "cgg_UG"
        chr = "chr"
        chr_US = "chr_US"
        cs = "cs"
        cs_CZ = "cs_CZ"
        cy = "cy"
        cy_GB = "cy_GB"
        da = "da"
        da_DK = "da_DK"
        dav = "dav"
        dav_KE = "dav_KE"
        de = "de"
        de_AT = "de_AT"
        de_BE = "de_BE"
        de_CH = "de_CH"
        de_DE = "de_DE"
        de_LI = "de_LI"
        de_LU = "de_LU"
        dje = "dje"
        dje_NE = "dje_NE"
        dua = "dua"
        dua_CM = "dua_CM"
        dyo = "dyo"
        dyo_SN = "dyo_SN"
        dz = "dz"
        dz_BT = "dz_BT"
        ebu = "ebu"
        ebu_KE = "ebu_KE"
        ee = "ee"
        ee_GH = "ee_GH"
        ee_TG = "ee_TG"
        el = "el"
        el_CY = "el_CY"
        el_GR = "el_GR"
        en = "en"
        en_150 = "en_150"
        en_AG = "en_AG"
        en_AS = "en_AS"
        en_AU = "en_AU"
        en_BB = "en_BB"
        en_BE = "en_BE"
        en_BM = "en_BM"
        en_BS = "en_BS"
        en_BW = "en_BW"
        en_BZ = "en_BZ"
        en_CA = "en_CA"
        en_CM = "en_CM"
        en_DM = "en_DM"
        en_FJ = "en_FJ"
        en_FM = "en_FM"
        en_GB = "en_GB"
        en_GD = "en_GD"
        en_GG = "en_GG"
        en_GH = "en_GH"
        en_GI = "en_GI"
        en_GM = "en_GM"
        en_GU = "en_GU"
        en_GY = "en_GY"
        en_HK = "en_HK"
        en_IE = "en_IE"
        en_IM = "en_IM"
        en_IN = "en_IN"
        en_JE = "en_JE"
        en_JM = "en_JM"
        en_KE = "en_KE"
        en_KI = "en_KI"
        en_KN = "en_KN"
        en_KY = "en_KY"
        en_LC = "en_LC"
        en_LR = "en_LR"
        en_LS = "en_LS"
        en_MG = "en_MG"
        en_MH = "en_MH"
        en_MP = "en_MP"
        en_MT = "en_MT"
        en_MU = "en_MU"
        en_MW = "en_MW"
        en_NA = "en_NA"
        en_NG = "en_NG"
        en_NZ = "en_NZ"
        en_PG = "en_PG"
        en_PH = "en_PH"
        en_PK = "en_PK"
        en_PR = "en_PR"
        en_PW = "en_PW"
        en_SB = "en_SB"
        en_SC = "en_SC"
        en_SG = "en_SG"
        en_SL = "en_SL"
        en_SS = "en_SS"
        en_SZ = "en_SZ"
        en_TC = "en_TC"
        en_TO = "en_TO"
        en_TT = "en_TT"
        en_TZ = "en_TZ"
        en_UG = "en_UG"
        en_UM = "en_UM"
        en_US = "en_US"
        en_US_POSIX = "en_US_POSIX"
        en_VC = "en_VC"
        en_VG = "en_VG"
        en_VI = "en_VI"
        en_VU = "en_VU"
        en_WS = "en_WS"
        en_ZA = "en_ZA"
        en_ZM = "en_ZM"
        en_ZW = "en_ZW"
        eo = "eo"
        es = "es"
        es_419 = "es_419"
        es_AR = "es_AR"
        es_BO = "es_BO"
        es_CL = "es_CL"
        es_CO = "es_CO"
        es_CR = "es_CR"
        es_CU = "es_CU"
        es_DO = "es_DO"
        es_EA = "es_EA"
        es_EC = "es_EC"
        es_ES = "es_ES"
        es_GQ = "es_GQ"
        es_GT = "es_GT"
        es_HN = "es_HN"
        es_IC = "es_IC"
        es_MX = "es_MX"
        es_NI = "es_NI"
        es_PA = "es_PA"
        es_PE = "es_PE"
        es_PH = "es_PH"
        es_PR = "es_PR"
        es_PY = "es_PY"
        es_SV = "es_SV"
        es_US = "es_US"
        es_UY = "es_UY"
        es_VE = "es_VE"
        et = "et"
        et_EE = "et_EE"
        eu = "eu"
        eu_ES = "eu_ES"
        ewo = "ewo"
        ewo_CM = "ewo_CM"
        fa = "fa"
        fa_AF = "fa_AF"
        fa_IR = "fa_IR"
        ff = "ff"
        ff_SN = "ff_SN"
        fi = "fi"
        fi_FI = "fi_FI"
        fil = "fil"
        fil_PH = "fil_PH"
        fo = "fo"
        fo_FO = "fo_FO"
        fr = "fr"
        fr_BE = "fr_BE"
        fr_BF = "fr_BF"
        fr_BI = "fr_BI"
        fr_BJ = "fr_BJ"
        fr_BL = "fr_BL"
        fr_CA = "fr_CA"
        fr_CD = "fr_CD"
        fr_CF = "fr_CF"
        fr_CG = "fr_CG"
        fr_CH = "fr_CH"
        fr_CI = "fr_CI"
        fr_CM = "fr_CM"
        fr_DJ = "fr_DJ"
        fr_DZ = "fr_DZ"
        fr_FR = "fr_FR"
        fr_GA = "fr_GA"
        fr_GF = "fr_GF"
        fr_GN = "fr_GN"
        fr_GP = "fr_GP"
        fr_GQ = "fr_GQ"
        fr_HT = "fr_HT"
        fr_KM = "fr_KM"
        fr_LU = "fr_LU"
        fr_MA = "fr_MA"
        fr_MC = "fr_MC"
        fr_MF = "fr_MF"
        fr_MG = "fr_MG"
        fr_ML = "fr_ML"
        fr_MQ = "fr_MQ"
        fr_MR = "fr_MR"
        fr_MU = "fr_MU"
        fr_NC = "fr_NC"
        fr_NE = "fr_NE"
        fr_PF = "fr_PF"
        fr_RE = "fr_RE"
        fr_RW = "fr_RW"
        fr_SC = "fr_SC"
        fr_SN = "fr_SN"
        fr_SY = "fr_SY"
        fr_TD = "fr_TD"
        fr_TG = "fr_TG"
        fr_TN = "fr_TN"
        fr_VU = "fr_VU"
        fr_YT = "fr_YT"
        ga = "ga"
        ga_IE = "ga_IE"
        gl = "gl"
        gl_ES = "gl_ES"
        gsw = "gsw"
        gsw_CH = "gsw_CH"
        gu = "gu"
        gu_IN = "gu_IN"
        guz = "guz"
        guz_KE = "guz_KE"
        gv = "gv"
        gv_GB = "gv_GB"
        ha = "ha"
        ha_Latn = "ha_Latn"
        ha_Latn_GH = "ha_Latn_GH"
        ha_Latn_NE = "ha_Latn_NE"
        ha_Latn_NG = "ha_Latn_NG"
        haw = "haw"
        haw_US = "haw_US"
        he = "he"
        he_IL = "he_IL"
        hi = "hi"
        hi_IN = "hi_IN"
        hr = "hr"
        hr_BA = "hr_BA"
        hr_HR = "hr_HR"
        hu = "hu"
        hu_HU = "hu_HU"
        hy = "hy"
        hy_AM = "hy_AM"
        id = "id"
        id_ID = "id_ID"
        ig = "ig"
        ig_NG = "ig_NG"
        ii = "ii"
        ii_CN = "ii_CN"
        is_ = "is"
        is_IS = "is_IS"
        it = "it"
        it_CH = "it_CH"
        it_IT = "it_IT"
        it_SM = "it_SM"
        ja = "ja"
        ja_JP = "ja_JP"
        jgo = "jgo"
        jgo_CM = "jgo_CM"
        jmc = "jmc"
        jmc_TZ = "jmc_TZ"
        ka = "ka"
        ka_GE = "ka_GE"
        kab = "kab"
        kab_DZ = "kab_DZ"
        kam = "kam"
        kam_KE = "kam_KE"
        kde = "kde"
        kde_TZ = "kde_TZ"
        kea = "kea"
        kea_CV = "kea_CV"
        khq = "khq"
        khq_ML = "khq_ML"
        ki = "ki"
        ki_KE = "ki_KE"
        kk = "kk"
        kk_Cyrl = "kk_Cyrl"
        kk_Cyrl_KZ = "kk_Cyrl_KZ"
        kl = "kl"
        kl_GL = "kl_GL"
        kln = "kln"
        kln_KE = "kln_KE"
        km = "km"
        km_KH = "km_KH"
        kn = "kn"
        kn_IN = "kn_IN"
        ko = "ko"
        ko_KP = "ko_KP"
        ko_KR = "ko_KR"
        kok = "kok"
        kok_IN = "kok_IN"
        ks = "ks"
        ks_Arab = "ks_Arab"
        ks_Arab_IN = "ks_Arab_IN"
        ksb = "ksb"
        ksb_TZ = "ksb_TZ"
        ksf = "ksf"
        ksf_CM = "ksf_CM"
        kw = "kw"
        kw_GB = "kw_GB"
        lag = "lag"
        lag_TZ = "lag_TZ"
        lg = "lg"
        lg_UG = "lg_UG"
        ln = "ln"
        ln_AO = "ln_AO"
        ln_CD = "ln_CD"
        ln_CF = "ln_CF"
        ln_CG = "ln_CG"
        lo = "lo"
        lo_LA = "lo_LA"
        lt = "lt"
        lt_LT = "lt_LT"
        lu = "lu"
        lu_CD = "lu_CD"
        luo = "luo"
        luo_KE = "luo_KE"
        luy = "luy"
        luy_KE = "luy_KE"
        lv = "lv"
        lv_LV = "lv_LV"
        mas = "mas"
        mas_KE = "mas_KE"
        mas_TZ = "mas_TZ"
        mer = "mer"
        mer_KE = "mer_KE"
        mfe = "mfe"
        mfe_MU = "mfe_MU"
        mg = "mg"
        mg_MG = "mg_MG"
        mgh = "mgh"
        mgh_MZ = "mgh_MZ"
        mgo = "mgo"
        mgo_CM = "mgo_CM"
        mk = "mk"
        mk_MK = "mk_MK"
        ml = "ml"
        ml_IN = "ml_IN"
        mr = "mr"
        mr_IN = "mr_IN"
        ms = "ms"
        ms_BN = "ms_BN"
        ms_MY = "ms_MY"
        ms_SG = "ms_SG"
        mt = "mt"
        mt_MT = "mt_MT"
        mua = "mua"
        mua_CM = "mua_CM"
        my = "my"
        my_MM = "my_MM"
        naq = "naq"
        naq_NA = "naq_NA"
        nb = "nb"
        nb_NO = "nb_NO"
        nd = "nd"
        nd_ZW = "nd_ZW"
        ne = "ne"
        ne_IN = "ne_IN"
        ne_NP = "ne_NP"
        nl = "nl"
        nl_AW = "nl_AW"
        nl_BE = "nl_BE"
        nl_CW = "nl_CW"
        nl_NL = "nl_NL"
        nl_SR = "nl_SR"
        nl_SX = "nl_SX"
        nmg = "nmg"
        nmg_CM = "nmg_CM"
        nn = "nn"
        nn_NO = "nn_NO"
        nus = "nus"
        nus_SD = "nus_SD"
        nyn = "nyn"
        nyn_UG = "nyn_UG"
        om = "om"
        om_ET = "om_ET"
        om_KE = "om_KE"
        or_ = "or"
        or_IN = "or_IN"
        pa = "pa"
        pa_Arab = "pa_Arab"
        pa_Arab_PK = "pa_Arab_PK"
        pa_Guru = "pa_Guru"
        pa_Guru_IN = "pa_Guru_IN"
        pl = "pl"
        pl_PL = "pl_PL"
        ps = "ps"
        ps_AF = "ps_AF"
        pt = "pt"
        pt_AO = "pt_AO"
        pt_BR = "pt_BR"
        pt_CV = "pt_CV"
        pt_GW = "pt_GW"
        pt_MO = "pt_MO"
        pt_MZ = "pt_MZ"
        pt_PT = "pt_PT"
        pt_ST = "pt_ST"
        pt_TL = "pt_TL"
        rm = "rm"
        rm_CH = "rm_CH"
        rn = "rn"
        rn_BI = "rn_BI"
        ro = "ro"
        ro_MD = "ro_MD"
        ro_RO = "ro_RO"
        rof = "rof"
        rof_TZ = "rof_TZ"
        ru = "ru"
        ru_BY = "ru_BY"
        ru_KG = "ru_KG"
        ru_KZ = "ru_KZ"
        ru_MD = "ru_MD"
        ru_RU = "ru_RU"
        ru_UA = "ru_UA"
        rw = "rw"
        rw_RW = "rw_RW"
        rwk = "rwk"
        rwk_TZ = "rwk_TZ"
        saq = "saq"
        saq_KE = "saq_KE"
        sbp = "sbp"
        sbp_TZ = "sbp_TZ"
        seh = "seh"
        seh_MZ = "seh_MZ"
        ses = "ses"
        ses_ML = "ses_ML"
        sg = "sg"
        sg_CF = "sg_CF"
        shi = "shi"
        shi_Latn = "shi_Latn"
        shi_Latn_MA = "shi_Latn_MA"
        shi_Tfng = "shi_Tfng"
        shi_Tfng_MA = "shi_Tfng_MA"
        si = "si"
        si_LK = "si_LK"
        sk = "sk"
        sk_SK = "sk_SK"
        sl = "sl"
        sl_SI = "sl_SI"
        sn = "sn"
        sn_ZW = "sn_ZW"
        so = "so"
        so_DJ = "so_DJ"
        so_ET = "so_ET"
        so_KE = "so_KE"
        so_SO = "so_SO"
        sq = "sq"
        sq_AL = "sq_AL"
        sq_MK = "sq_MK"
        sr = "sr"
        sr_Cyrl = "sr_Cyrl"
        sr_Cyrl_BA = "sr_Cyrl_BA"
        sr_Cyrl_ME = "sr_Cyrl_ME"
        sr_Cyrl_RS = "sr_Cyrl_RS"
        sr_Latn = "sr_Latn"
        sr_Latn_BA = "sr_Latn_BA"
        sr_Latn_ME = "sr_Latn_ME"
        sr_Latn_RS = "sr_Latn_RS"
        sv = "sv"
        sv_AX = "sv_AX"
        sv_FI = "sv_FI"
        sv_SE = "sv_SE"
        sw = "sw"
        sw_KE = "sw_KE"
        sw_TZ = "sw_TZ"
        sw_UG = "sw_UG"
        swc = "swc"
        swc_CD = "swc_CD"
        ta = "ta"
        ta_IN = "ta_IN"
        ta_LK = "ta_LK"
        ta_MY = "ta_MY"
        ta_SG = "ta_SG"
        te = "te"
        te_IN = "te_IN"
        teo = "teo"
        teo_KE = "teo_KE"
        teo_UG = "teo_UG"
        th = "th"
        th_TH = "th_TH"
        ti = "ti"
        ti_ER = "ti_ER"
        ti_ET = "ti_ET"
        to = "to"
        to_TO = "to_TO"
        tr = "tr"
        tr_CY = "tr_CY"
        tr_TR = "tr_TR"
        twq = "twq"
        twq_NE = "twq_NE"
        tzm = "tzm"
        tzm_Latn = "tzm_Latn"
        tzm_Latn_MA = "tzm_Latn_MA"
        uk = "uk"
        uk_UA = "uk_UA"
        ur = "ur"
        ur_IN = "ur_IN"
        ur_PK = "ur_PK"
        uz = "uz"
        uz_Arab = "uz_Arab"
        uz_Arab_AF = "uz_Arab_AF"
        uz_Cyrl = "uz_Cyrl"
        uz_Cyrl_UZ = "uz_Cyrl_UZ"
        uz_Latn = "uz_Latn"
        uz_Latn_UZ = "uz_Latn_UZ"
        vai = "vai"
        vai_Latn = "vai_Latn"
        vai_Latn_LR = "vai_Latn_LR"
        vai_Vaii = "vai_Vaii"
        vai_Vaii_LR = "vai_Vaii_LR"
        vi = "vi"
        vi_VN = "vi_VN"
        vun = "vun"
        vun_TZ = "vun_TZ"
        xog = "xog"
        xog_UG = "xog_UG"
        yav = "yav"
        yav_CM = "yav_CM"
        yo = "yo"
        yo_NG = "yo_NG"
        zh = "zh"
        zh_Hans = "zh_Hans"
        zh_Hans_CN = "zh_Hans_CN"
        zh_Hans_HK = "zh_Hans_HK"
        zh_Hans_MO = "zh_Hans_MO"
        zh_Hans_SG = "zh_Hans_SG"
        zh_Hant = "zh_Hant"
        zh_Hant_HK = "zh_Hant_HK"
        zh_Hant_MO = "zh_Hant_MO"
        zh_Hant_TW = "zh_Hant_TW"
        zu = "zu"
        zu_ZA = "zu_ZA"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class WAVE_GENERATOR:
    """Enums for properties in the WAVE_GENERATOR stage."""

    class Mode(Enum):
        """Enum for the Mode property."""

        column = "column"
        count = "count"
        dupkey = "dupkey"

    class Sequence(Enum):
        """Enum for the Sequence property."""

        before = "before"
        after = "after"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class COLUMN_GENERATOR:
    """Enums for properties in the COLUMN_GENERATOR stage."""

    class Selection(Enum):
        """Enum for the Selection property."""

        file = "file"
        explicit = "explicit"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class TWO_SOURCE_MATCH:
    """Enums for properties in the TWO_SOURCE_MATCH stage."""

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class Pgmtype(Enum):
        """Enum for the Pgmtype property."""

        many_to_one = "Many-to-one"
        many_to_one_multiple = "Many-to-one multiple"
        many_to_one_duplicate = "Many-to-one duplicate"
        one_to_one = "One-to-one"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class Db2NameSelect(Enum):
        """Enum for the Db2NameSelect property."""

        use_db2NameEnv = "use_db2NameEnv"
        use_userDefinedName = "use_userDefinedName"

    class Db2InstanceSelect(Enum):
        """Enum for the Db2InstanceSelect property."""

        use_db2InstanceEnv = "use_db2InstanceEnv"
        use_userDefinedInstance = "use_userDefinedInstance"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        Select_a_column = "Select a column"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class DATASET:
    """Enums for properties in the DATASET stage."""

    class UpdatePolicy(Enum):
        """Enum for the UpdatePolicy property."""

        discard_records = "> [ds; -dr"
        overwrite = ">| [ds"
        append = ">> [ds"
        discard_schema = "> [ds; -dsr"
        create = "> [ds"

    class MissingColumnsMode(Enum):
        """Enum for the MissingColumnsMode property."""

        nonnullable = "nonnullable"
        nullable = "nullable"
        custom = " "
        all = "all"
        fail = "fail"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class TRANSFORMER:
    """Enums for properties in the TRANSFORMER stage."""

    class SKKeySourceType(Enum):
        """Enum for the SKKeySourceType property."""

        file = "file"
        dbsequence = "dbsequence"

    class BlockSizeSelectedType(Enum):
        """Enum for the BlockSizeSelectedType property."""

        systemSelected = "systemSelected"
        manualSelected = "manualSelected"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class CollationSequence(Enum):
        """Enum for the CollationSequence property."""

        OFF = "OFF"
        af = "af"
        af_NA = "af_NA"
        af_ZA = "af_ZA"
        agq = "agq"
        agq_CM = "agq_CM"
        ak = "ak"
        ak_GH = "ak_GH"
        am = "am"
        am_ET = "am_ET"
        ar = "ar"
        ar_001 = "ar_001"
        ar_AE = "ar_AE"
        ar_BH = "ar_BH"
        ar_DJ = "ar_DJ"
        ar_DZ = "ar_DZ"
        ar_EG = "ar_EG"
        ar_EH = "ar_EH"
        ar_ER = "ar_ER"
        ar_IL = "ar_IL"
        ar_IQ = "ar_IQ"
        ar_JO = "ar_JO"
        ar_KM = "ar_KM"
        ar_KW = "ar_KW"
        ar_LB = "ar_LB"
        ar_LY = "ar_LY"
        ar_MA = "ar_MA"
        ar_MR = "ar_MR"
        ar_OM = "ar_OM"
        ar_PS = "ar_PS"
        ar_QA = "ar_QA"
        ar_SA = "ar_SA"
        ar_SD = "ar_SD"
        ar_SO = "ar_SO"
        ar_SY = "ar_SY"
        ar_TD = "ar_TD"
        ar_TN = "ar_TN"
        ar_YE = "ar_YE"
        as_ = "as"
        as_IN = "as_IN"
        asa = "asa"
        asa_TZ = "asa_TZ"
        az = "az"
        az_Cyrl = "az_Cyrl"
        az_Cyrl_AZ = "az_Cyrl_AZ"
        az_Latn = "az_Latn"
        az_Latn_AZ = "az_Latn_AZ"
        bas = "bas"
        bas_CM = "bas_CM"
        be = "be"
        be_BY = "be_BY"
        bem = "bem"
        bem_ZM = "bem_ZM"
        bez = "bez"
        bez_TZ = "bez_TZ"
        bg = "bg"
        bg_BG = "bg_BG"
        bm = "bm"
        bm_ML = "bm_ML"
        bn = "bn"
        bn_BD = "bn_BD"
        bn_IN = "bn_IN"
        bo = "bo"
        bo_CN = "bo_CN"
        bo_IN = "bo_IN"
        br = "br"
        br_FR = "br_FR"
        brx = "brx"
        brx_IN = "brx_IN"
        bs = "bs"
        bs_Cyrl = "bs_Cyrl"
        bs_Cyrl_BA = "bs_Cyrl_BA"
        bs_Latn = "bs_Latn"
        bs_Latn_BA = "bs_Latn_BA"
        ca = "ca"
        ca_AD = "ca_AD"
        ca_ES = "ca_ES"
        cgg = "cgg"
        cgg_UG = "cgg_UG"
        chr = "chr"
        chr_US = "chr_US"
        cs = "cs"
        cs_CZ = "cs_CZ"
        cy = "cy"
        cy_GB = "cy_GB"
        da = "da"
        da_DK = "da_DK"
        dav = "dav"
        dav_KE = "dav_KE"
        de = "de"
        de_AT = "de_AT"
        de_BE = "de_BE"
        de_CH = "de_CH"
        de_DE = "de_DE"
        de_LI = "de_LI"
        de_LU = "de_LU"
        dje = "dje"
        dje_NE = "dje_NE"
        dua = "dua"
        dua_CM = "dua_CM"
        dyo = "dyo"
        dyo_SN = "dyo_SN"
        dz = "dz"
        dz_BT = "dz_BT"
        ebu = "ebu"
        ebu_KE = "ebu_KE"
        ee = "ee"
        ee_GH = "ee_GH"
        ee_TG = "ee_TG"
        el = "el"
        el_CY = "el_CY"
        el_GR = "el_GR"
        en = "en"
        en_150 = "en_150"
        en_AG = "en_AG"
        en_AS = "en_AS"
        en_AU = "en_AU"
        en_BB = "en_BB"
        en_BE = "en_BE"
        en_BM = "en_BM"
        en_BS = "en_BS"
        en_BW = "en_BW"
        en_BZ = "en_BZ"
        en_CA = "en_CA"
        en_CM = "en_CM"
        en_DM = "en_DM"
        en_FJ = "en_FJ"
        en_FM = "en_FM"
        en_GB = "en_GB"
        en_GD = "en_GD"
        en_GG = "en_GG"
        en_GH = "en_GH"
        en_GI = "en_GI"
        en_GM = "en_GM"
        en_GU = "en_GU"
        en_GY = "en_GY"
        en_HK = "en_HK"
        en_IE = "en_IE"
        en_IM = "en_IM"
        en_IN = "en_IN"
        en_JE = "en_JE"
        en_JM = "en_JM"
        en_KE = "en_KE"
        en_KI = "en_KI"
        en_KN = "en_KN"
        en_KY = "en_KY"
        en_LC = "en_LC"
        en_LR = "en_LR"
        en_LS = "en_LS"
        en_MG = "en_MG"
        en_MH = "en_MH"
        en_MP = "en_MP"
        en_MT = "en_MT"
        en_MU = "en_MU"
        en_MW = "en_MW"
        en_NA = "en_NA"
        en_NG = "en_NG"
        en_NZ = "en_NZ"
        en_PG = "en_PG"
        en_PH = "en_PH"
        en_PK = "en_PK"
        en_PR = "en_PR"
        en_PW = "en_PW"
        en_SB = "en_SB"
        en_SC = "en_SC"
        en_SG = "en_SG"
        en_SL = "en_SL"
        en_SS = "en_SS"
        en_SZ = "en_SZ"
        en_TC = "en_TC"
        en_TO = "en_TO"
        en_TT = "en_TT"
        en_TZ = "en_TZ"
        en_UG = "en_UG"
        en_UM = "en_UM"
        en_US = "en_US"
        en_US_POSIX = "en_US_POSIX"
        en_VC = "en_VC"
        en_VG = "en_VG"
        en_VI = "en_VI"
        en_VU = "en_VU"
        en_WS = "en_WS"
        en_ZA = "en_ZA"
        en_ZM = "en_ZM"
        en_ZW = "en_ZW"
        eo = "eo"
        es = "es"
        es_419 = "es_419"
        es_AR = "es_AR"
        es_BO = "es_BO"
        es_CL = "es_CL"
        es_CO = "es_CO"
        es_CR = "es_CR"
        es_CU = "es_CU"
        es_DO = "es_DO"
        es_EA = "es_EA"
        es_EC = "es_EC"
        es_ES = "es_ES"
        es_GQ = "es_GQ"
        es_GT = "es_GT"
        es_HN = "es_HN"
        es_IC = "es_IC"
        es_MX = "es_MX"
        es_NI = "es_NI"
        es_PA = "es_PA"
        es_PE = "es_PE"
        es_PH = "es_PH"
        es_PR = "es_PR"
        es_PY = "es_PY"
        es_SV = "es_SV"
        es_US = "es_US"
        es_UY = "es_UY"
        es_VE = "es_VE"
        et = "et"
        et_EE = "et_EE"
        eu = "eu"
        eu_ES = "eu_ES"
        ewo = "ewo"
        ewo_CM = "ewo_CM"
        fa = "fa"
        fa_AF = "fa_AF"
        fa_IR = "fa_IR"
        ff = "ff"
        ff_SN = "ff_SN"
        fi = "fi"
        fi_FI = "fi_FI"
        fil = "fil"
        fil_PH = "fil_PH"
        fo = "fo"
        fo_FO = "fo_FO"
        fr = "fr"
        fr_BE = "fr_BE"
        fr_BF = "fr_BF"
        fr_BI = "fr_BI"
        fr_BJ = "fr_BJ"
        fr_BL = "fr_BL"
        fr_CA = "fr_CA"
        fr_CD = "fr_CD"
        fr_CF = "fr_CF"
        fr_CG = "fr_CG"
        fr_CH = "fr_CH"
        fr_CI = "fr_CI"
        fr_CM = "fr_CM"
        fr_DJ = "fr_DJ"
        fr_DZ = "fr_DZ"
        fr_FR = "fr_FR"
        fr_GA = "fr_GA"
        fr_GF = "fr_GF"
        fr_GN = "fr_GN"
        fr_GP = "fr_GP"
        fr_GQ = "fr_GQ"
        fr_HT = "fr_HT"
        fr_KM = "fr_KM"
        fr_LU = "fr_LU"
        fr_MA = "fr_MA"
        fr_MC = "fr_MC"
        fr_MF = "fr_MF"
        fr_MG = "fr_MG"
        fr_ML = "fr_ML"
        fr_MQ = "fr_MQ"
        fr_MR = "fr_MR"
        fr_MU = "fr_MU"
        fr_NC = "fr_NC"
        fr_NE = "fr_NE"
        fr_PF = "fr_PF"
        fr_RE = "fr_RE"
        fr_RW = "fr_RW"
        fr_SC = "fr_SC"
        fr_SN = "fr_SN"
        fr_SY = "fr_SY"
        fr_TD = "fr_TD"
        fr_TG = "fr_TG"
        fr_TN = "fr_TN"
        fr_VU = "fr_VU"
        fr_YT = "fr_YT"
        ga = "ga"
        ga_IE = "ga_IE"
        gl = "gl"
        gl_ES = "gl_ES"
        gsw = "gsw"
        gsw_CH = "gsw_CH"
        gu = "gu"
        gu_IN = "gu_IN"
        guz = "guz"
        guz_KE = "guz_KE"
        gv = "gv"
        gv_GB = "gv_GB"
        ha = "ha"
        ha_Latn = "ha_Latn"
        ha_Latn_GH = "ha_Latn_GH"
        ha_Latn_NE = "ha_Latn_NE"
        ha_Latn_NG = "ha_Latn_NG"
        haw = "haw"
        haw_US = "haw_US"
        he = "he"
        he_IL = "he_IL"
        hi = "hi"
        hi_IN = "hi_IN"
        hr = "hr"
        hr_BA = "hr_BA"
        hr_HR = "hr_HR"
        hu = "hu"
        hu_HU = "hu_HU"
        hy = "hy"
        hy_AM = "hy_AM"
        id = "id"
        id_ID = "id_ID"
        ig = "ig"
        ig_NG = "ig_NG"
        ii = "ii"
        ii_CN = "ii_CN"
        is_ = "is"
        is_IS = "is_IS"
        it = "it"
        it_CH = "it_CH"
        it_IT = "it_IT"
        it_SM = "it_SM"
        ja = "ja"
        ja_JP = "ja_JP"
        jgo = "jgo"
        jgo_CM = "jgo_CM"
        jmc = "jmc"
        jmc_TZ = "jmc_TZ"
        ka = "ka"
        ka_GE = "ka_GE"
        kab = "kab"
        kab_DZ = "kab_DZ"
        kam = "kam"
        kam_KE = "kam_KE"
        kde = "kde"
        kde_TZ = "kde_TZ"
        kea = "kea"
        kea_CV = "kea_CV"
        khq = "khq"
        khq_ML = "khq_ML"
        ki = "ki"
        ki_KE = "ki_KE"
        kk = "kk"
        kk_Cyrl = "kk_Cyrl"
        kk_Cyrl_KZ = "kk_Cyrl_KZ"
        kl = "kl"
        kl_GL = "kl_GL"
        kln = "kln"
        kln_KE = "kln_KE"
        km = "km"
        km_KH = "km_KH"
        kn = "kn"
        kn_IN = "kn_IN"
        ko = "ko"
        ko_KP = "ko_KP"
        ko_KR = "ko_KR"
        kok = "kok"
        kok_IN = "kok_IN"
        ks = "ks"
        ks_Arab = "ks_Arab"
        ks_Arab_IN = "ks_Arab_IN"
        ksb = "ksb"
        ksb_TZ = "ksb_TZ"
        ksf = "ksf"
        ksf_CM = "ksf_CM"
        kw = "kw"
        kw_GB = "kw_GB"
        lag = "lag"
        lag_TZ = "lag_TZ"
        lg = "lg"
        lg_UG = "lg_UG"
        ln = "ln"
        ln_AO = "ln_AO"
        ln_CD = "ln_CD"
        ln_CF = "ln_CF"
        ln_CG = "ln_CG"
        lo = "lo"
        lo_LA = "lo_LA"
        lt = "lt"
        lt_LT = "lt_LT"
        lu = "lu"
        lu_CD = "lu_CD"
        luo = "luo"
        luo_KE = "luo_KE"
        luy = "luy"
        luy_KE = "luy_KE"
        lv = "lv"
        lv_LV = "lv_LV"
        mas = "mas"
        mas_KE = "mas_KE"
        mas_TZ = "mas_TZ"
        mer = "mer"
        mer_KE = "mer_KE"
        mfe = "mfe"
        mfe_MU = "mfe_MU"
        mg = "mg"
        mg_MG = "mg_MG"
        mgh = "mgh"
        mgh_MZ = "mgh_MZ"
        mgo = "mgo"
        mgo_CM = "mgo_CM"
        mk = "mk"
        mk_MK = "mk_MK"
        ml = "ml"
        ml_IN = "ml_IN"
        mr = "mr"
        mr_IN = "mr_IN"
        ms = "ms"
        ms_BN = "ms_BN"
        ms_MY = "ms_MY"
        ms_SG = "ms_SG"
        mt = "mt"
        mt_MT = "mt_MT"
        mua = "mua"
        mua_CM = "mua_CM"
        my = "my"
        my_MM = "my_MM"
        naq = "naq"
        naq_NA = "naq_NA"
        nb = "nb"
        nb_NO = "nb_NO"
        nd = "nd"
        nd_ZW = "nd_ZW"
        ne = "ne"
        ne_IN = "ne_IN"
        ne_NP = "ne_NP"
        nl = "nl"
        nl_AW = "nl_AW"
        nl_BE = "nl_BE"
        nl_CW = "nl_CW"
        nl_NL = "nl_NL"
        nl_SR = "nl_SR"
        nl_SX = "nl_SX"
        nmg = "nmg"
        nmg_CM = "nmg_CM"
        nn = "nn"
        nn_NO = "nn_NO"
        nus = "nus"
        nus_SD = "nus_SD"
        nyn = "nyn"
        nyn_UG = "nyn_UG"
        om = "om"
        om_ET = "om_ET"
        om_KE = "om_KE"
        or_ = "or"
        or_IN = "or_IN"
        pa = "pa"
        pa_Arab = "pa_Arab"
        pa_Arab_PK = "pa_Arab_PK"
        pa_Guru = "pa_Guru"
        pa_Guru_IN = "pa_Guru_IN"
        pl = "pl"
        pl_PL = "pl_PL"
        ps = "ps"
        ps_AF = "ps_AF"
        pt = "pt"
        pt_AO = "pt_AO"
        pt_BR = "pt_BR"
        pt_CV = "pt_CV"
        pt_GW = "pt_GW"
        pt_MO = "pt_MO"
        pt_MZ = "pt_MZ"
        pt_PT = "pt_PT"
        pt_ST = "pt_ST"
        pt_TL = "pt_TL"
        rm = "rm"
        rm_CH = "rm_CH"
        rn = "rn"
        rn_BI = "rn_BI"
        ro = "ro"
        ro_MD = "ro_MD"
        ro_RO = "ro_RO"
        rof = "rof"
        rof_TZ = "rof_TZ"
        ru = "ru"
        ru_BY = "ru_BY"
        ru_KG = "ru_KG"
        ru_KZ = "ru_KZ"
        ru_MD = "ru_MD"
        ru_RU = "ru_RU"
        ru_UA = "ru_UA"
        rw = "rw"
        rw_RW = "rw_RW"
        rwk = "rwk"
        rwk_TZ = "rwk_TZ"
        saq = "saq"
        saq_KE = "saq_KE"
        sbp = "sbp"
        sbp_TZ = "sbp_TZ"
        seh = "seh"
        seh_MZ = "seh_MZ"
        ses = "ses"
        ses_ML = "ses_ML"
        sg = "sg"
        sg_CF = "sg_CF"
        shi = "shi"
        shi_Latn = "shi_Latn"
        shi_Latn_MA = "shi_Latn_MA"
        shi_Tfng = "shi_Tfng"
        shi_Tfng_MA = "shi_Tfng_MA"
        si = "si"
        si_LK = "si_LK"
        sk = "sk"
        sk_SK = "sk_SK"
        sl = "sl"
        sl_SI = "sl_SI"
        sn = "sn"
        sn_ZW = "sn_ZW"
        so = "so"
        so_DJ = "so_DJ"
        so_ET = "so_ET"
        so_KE = "so_KE"
        so_SO = "so_SO"
        sq = "sq"
        sq_AL = "sq_AL"
        sq_MK = "sq_MK"
        sr = "sr"
        sr_Cyrl = "sr_Cyrl"
        sr_Cyrl_BA = "sr_Cyrl_BA"
        sr_Cyrl_ME = "sr_Cyrl_ME"
        sr_Cyrl_RS = "sr_Cyrl_RS"
        sr_Latn = "sr_Latn"
        sr_Latn_BA = "sr_Latn_BA"
        sr_Latn_ME = "sr_Latn_ME"
        sr_Latn_RS = "sr_Latn_RS"
        sv = "sv"
        sv_AX = "sv_AX"
        sv_FI = "sv_FI"
        sv_SE = "sv_SE"
        sw = "sw"
        sw_KE = "sw_KE"
        sw_TZ = "sw_TZ"
        sw_UG = "sw_UG"
        swc = "swc"
        swc_CD = "swc_CD"
        ta = "ta"
        ta_IN = "ta_IN"
        ta_LK = "ta_LK"
        ta_MY = "ta_MY"
        ta_SG = "ta_SG"
        te = "te"
        te_IN = "te_IN"
        teo = "teo"
        teo_KE = "teo_KE"
        teo_UG = "teo_UG"
        th = "th"
        th_TH = "th_TH"
        ti = "ti"
        ti_ER = "ti_ER"
        ti_ET = "ti_ET"
        to = "to"
        to_TO = "to_TO"
        tr = "tr"
        tr_CY = "tr_CY"
        tr_TR = "tr_TR"
        twq = "twq"
        twq_NE = "twq_NE"
        tzm = "tzm"
        tzm_Latn = "tzm_Latn"
        tzm_Latn_MA = "tzm_Latn_MA"
        uk = "uk"
        uk_UA = "uk_UA"
        ur = "ur"
        ur_IN = "ur_IN"
        ur_PK = "ur_PK"
        uz = "uz"
        uz_Arab = "uz_Arab"
        uz_Arab_AF = "uz_Arab_AF"
        uz_Cyrl = "uz_Cyrl"
        uz_Cyrl_UZ = "uz_Cyrl_UZ"
        uz_Latn = "uz_Latn"
        uz_Latn_UZ = "uz_Latn_UZ"
        vai = "vai"
        vai_Latn = "vai_Latn"
        vai_Latn_LR = "vai_Latn_LR"
        vai_Vaii = "vai_Vaii"
        vai_Vaii_LR = "vai_Vaii_LR"
        vi = "vi"
        vi_VN = "vi_VN"
        vun = "vun"
        vun_TZ = "vun_TZ"
        xog = "xog"
        xog_UG = "xog_UG"
        yav = "yav"
        yav_CM = "yav_CM"
        yo = "yo"
        yo_NG = "yo_NG"
        zh = "zh"
        zh_Hans = "zh_Hans"
        zh_Hans_CN = "zh_Hans_CN"
        zh_Hans_HK = "zh_Hans_HK"
        zh_Hans_MO = "zh_Hans_MO"
        zh_Hans_SG = "zh_Hans_SG"
        zh_Hant = "zh_Hant"
        zh_Hant_HK = "zh_Hant_HK"
        zh_Hant_MO = "zh_Hant_MO"
        zh_Hant_TW = "zh_Hant_TW"
        zu = "zu"
        zu_ZA = "zu_ZA"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class JOIN:
    """Enums for properties in the JOIN stage."""

    class Operator(Enum):
        """Enum for the Operator property."""

        innerjoin = "innerjoin"
        leftouterjoin = "leftouterjoin"
        rightouterjoin = "rightouterjoin"
        fullouterjoin = "fullouterjoin"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class CollationSequence(Enum):
        """Enum for the CollationSequence property."""

        OFF = "OFF"
        af = "af"
        af_NA = "af_NA"
        af_ZA = "af_ZA"
        agq = "agq"
        agq_CM = "agq_CM"
        ak = "ak"
        ak_GH = "ak_GH"
        am = "am"
        am_ET = "am_ET"
        ar = "ar"
        ar_001 = "ar_001"
        ar_AE = "ar_AE"
        ar_BH = "ar_BH"
        ar_DJ = "ar_DJ"
        ar_DZ = "ar_DZ"
        ar_EG = "ar_EG"
        ar_EH = "ar_EH"
        ar_ER = "ar_ER"
        ar_IL = "ar_IL"
        ar_IQ = "ar_IQ"
        ar_JO = "ar_JO"
        ar_KM = "ar_KM"
        ar_KW = "ar_KW"
        ar_LB = "ar_LB"
        ar_LY = "ar_LY"
        ar_MA = "ar_MA"
        ar_MR = "ar_MR"
        ar_OM = "ar_OM"
        ar_PS = "ar_PS"
        ar_QA = "ar_QA"
        ar_SA = "ar_SA"
        ar_SD = "ar_SD"
        ar_SO = "ar_SO"
        ar_SY = "ar_SY"
        ar_TD = "ar_TD"
        ar_TN = "ar_TN"
        ar_YE = "ar_YE"
        as_ = "as"
        as_IN = "as_IN"
        asa = "asa"
        asa_TZ = "asa_TZ"
        az = "az"
        az_Cyrl = "az_Cyrl"
        az_Cyrl_AZ = "az_Cyrl_AZ"
        az_Latn = "az_Latn"
        az_Latn_AZ = "az_Latn_AZ"
        bas = "bas"
        bas_CM = "bas_CM"
        be = "be"
        be_BY = "be_BY"
        bem = "bem"
        bem_ZM = "bem_ZM"
        bez = "bez"
        bez_TZ = "bez_TZ"
        bg = "bg"
        bg_BG = "bg_BG"
        bm = "bm"
        bm_ML = "bm_ML"
        bn = "bn"
        bn_BD = "bn_BD"
        bn_IN = "bn_IN"
        bo = "bo"
        bo_CN = "bo_CN"
        bo_IN = "bo_IN"
        br = "br"
        br_FR = "br_FR"
        brx = "brx"
        brx_IN = "brx_IN"
        bs = "bs"
        bs_Cyrl = "bs_Cyrl"
        bs_Cyrl_BA = "bs_Cyrl_BA"
        bs_Latn = "bs_Latn"
        bs_Latn_BA = "bs_Latn_BA"
        ca = "ca"
        ca_AD = "ca_AD"
        ca_ES = "ca_ES"
        cgg = "cgg"
        cgg_UG = "cgg_UG"
        chr = "chr"
        chr_US = "chr_US"
        cs = "cs"
        cs_CZ = "cs_CZ"
        cy = "cy"
        cy_GB = "cy_GB"
        da = "da"
        da_DK = "da_DK"
        dav = "dav"
        dav_KE = "dav_KE"
        de = "de"
        de_AT = "de_AT"
        de_BE = "de_BE"
        de_CH = "de_CH"
        de_DE = "de_DE"
        de_LI = "de_LI"
        de_LU = "de_LU"
        dje = "dje"
        dje_NE = "dje_NE"
        dua = "dua"
        dua_CM = "dua_CM"
        dyo = "dyo"
        dyo_SN = "dyo_SN"
        dz = "dz"
        dz_BT = "dz_BT"
        ebu = "ebu"
        ebu_KE = "ebu_KE"
        ee = "ee"
        ee_GH = "ee_GH"
        ee_TG = "ee_TG"
        el = "el"
        el_CY = "el_CY"
        el_GR = "el_GR"
        en = "en"
        en_150 = "en_150"
        en_AG = "en_AG"
        en_AS = "en_AS"
        en_AU = "en_AU"
        en_BB = "en_BB"
        en_BE = "en_BE"
        en_BM = "en_BM"
        en_BS = "en_BS"
        en_BW = "en_BW"
        en_BZ = "en_BZ"
        en_CA = "en_CA"
        en_CM = "en_CM"
        en_DM = "en_DM"
        en_FJ = "en_FJ"
        en_FM = "en_FM"
        en_GB = "en_GB"
        en_GD = "en_GD"
        en_GG = "en_GG"
        en_GH = "en_GH"
        en_GI = "en_GI"
        en_GM = "en_GM"
        en_GU = "en_GU"
        en_GY = "en_GY"
        en_HK = "en_HK"
        en_IE = "en_IE"
        en_IM = "en_IM"
        en_IN = "en_IN"
        en_JE = "en_JE"
        en_JM = "en_JM"
        en_KE = "en_KE"
        en_KI = "en_KI"
        en_KN = "en_KN"
        en_KY = "en_KY"
        en_LC = "en_LC"
        en_LR = "en_LR"
        en_LS = "en_LS"
        en_MG = "en_MG"
        en_MH = "en_MH"
        en_MP = "en_MP"
        en_MT = "en_MT"
        en_MU = "en_MU"
        en_MW = "en_MW"
        en_NA = "en_NA"
        en_NG = "en_NG"
        en_NZ = "en_NZ"
        en_PG = "en_PG"
        en_PH = "en_PH"
        en_PK = "en_PK"
        en_PR = "en_PR"
        en_PW = "en_PW"
        en_SB = "en_SB"
        en_SC = "en_SC"
        en_SG = "en_SG"
        en_SL = "en_SL"
        en_SS = "en_SS"
        en_SZ = "en_SZ"
        en_TC = "en_TC"
        en_TO = "en_TO"
        en_TT = "en_TT"
        en_TZ = "en_TZ"
        en_UG = "en_UG"
        en_UM = "en_UM"
        en_US = "en_US"
        en_US_POSIX = "en_US_POSIX"
        en_VC = "en_VC"
        en_VG = "en_VG"
        en_VI = "en_VI"
        en_VU = "en_VU"
        en_WS = "en_WS"
        en_ZA = "en_ZA"
        en_ZM = "en_ZM"
        en_ZW = "en_ZW"
        eo = "eo"
        es = "es"
        es_419 = "es_419"
        es_AR = "es_AR"
        es_BO = "es_BO"
        es_CL = "es_CL"
        es_CO = "es_CO"
        es_CR = "es_CR"
        es_CU = "es_CU"
        es_DO = "es_DO"
        es_EA = "es_EA"
        es_EC = "es_EC"
        es_ES = "es_ES"
        es_GQ = "es_GQ"
        es_GT = "es_GT"
        es_HN = "es_HN"
        es_IC = "es_IC"
        es_MX = "es_MX"
        es_NI = "es_NI"
        es_PA = "es_PA"
        es_PE = "es_PE"
        es_PH = "es_PH"
        es_PR = "es_PR"
        es_PY = "es_PY"
        es_SV = "es_SV"
        es_US = "es_US"
        es_UY = "es_UY"
        es_VE = "es_VE"
        et = "et"
        et_EE = "et_EE"
        eu = "eu"
        eu_ES = "eu_ES"
        ewo = "ewo"
        ewo_CM = "ewo_CM"
        fa = "fa"
        fa_AF = "fa_AF"
        fa_IR = "fa_IR"
        ff = "ff"
        ff_SN = "ff_SN"
        fi = "fi"
        fi_FI = "fi_FI"
        fil = "fil"
        fil_PH = "fil_PH"
        fo = "fo"
        fo_FO = "fo_FO"
        fr = "fr"
        fr_BE = "fr_BE"
        fr_BF = "fr_BF"
        fr_BI = "fr_BI"
        fr_BJ = "fr_BJ"
        fr_BL = "fr_BL"
        fr_CA = "fr_CA"
        fr_CD = "fr_CD"
        fr_CF = "fr_CF"
        fr_CG = "fr_CG"
        fr_CH = "fr_CH"
        fr_CI = "fr_CI"
        fr_CM = "fr_CM"
        fr_DJ = "fr_DJ"
        fr_DZ = "fr_DZ"
        fr_FR = "fr_FR"
        fr_GA = "fr_GA"
        fr_GF = "fr_GF"
        fr_GN = "fr_GN"
        fr_GP = "fr_GP"
        fr_GQ = "fr_GQ"
        fr_HT = "fr_HT"
        fr_KM = "fr_KM"
        fr_LU = "fr_LU"
        fr_MA = "fr_MA"
        fr_MC = "fr_MC"
        fr_MF = "fr_MF"
        fr_MG = "fr_MG"
        fr_ML = "fr_ML"
        fr_MQ = "fr_MQ"
        fr_MR = "fr_MR"
        fr_MU = "fr_MU"
        fr_NC = "fr_NC"
        fr_NE = "fr_NE"
        fr_PF = "fr_PF"
        fr_RE = "fr_RE"
        fr_RW = "fr_RW"
        fr_SC = "fr_SC"
        fr_SN = "fr_SN"
        fr_SY = "fr_SY"
        fr_TD = "fr_TD"
        fr_TG = "fr_TG"
        fr_TN = "fr_TN"
        fr_VU = "fr_VU"
        fr_YT = "fr_YT"
        ga = "ga"
        ga_IE = "ga_IE"
        gl = "gl"
        gl_ES = "gl_ES"
        gsw = "gsw"
        gsw_CH = "gsw_CH"
        gu = "gu"
        gu_IN = "gu_IN"
        guz = "guz"
        guz_KE = "guz_KE"
        gv = "gv"
        gv_GB = "gv_GB"
        ha = "ha"
        ha_Latn = "ha_Latn"
        ha_Latn_GH = "ha_Latn_GH"
        ha_Latn_NE = "ha_Latn_NE"
        ha_Latn_NG = "ha_Latn_NG"
        haw = "haw"
        haw_US = "haw_US"
        he = "he"
        he_IL = "he_IL"
        hi = "hi"
        hi_IN = "hi_IN"
        hr = "hr"
        hr_BA = "hr_BA"
        hr_HR = "hr_HR"
        hu = "hu"
        hu_HU = "hu_HU"
        hy = "hy"
        hy_AM = "hy_AM"
        id = "id"
        id_ID = "id_ID"
        ig = "ig"
        ig_NG = "ig_NG"
        ii = "ii"
        ii_CN = "ii_CN"
        is_ = "is"
        is_IS = "is_IS"
        it = "it"
        it_CH = "it_CH"
        it_IT = "it_IT"
        it_SM = "it_SM"
        ja = "ja"
        ja_JP = "ja_JP"
        jgo = "jgo"
        jgo_CM = "jgo_CM"
        jmc = "jmc"
        jmc_TZ = "jmc_TZ"
        ka = "ka"
        ka_GE = "ka_GE"
        kab = "kab"
        kab_DZ = "kab_DZ"
        kam = "kam"
        kam_KE = "kam_KE"
        kde = "kde"
        kde_TZ = "kde_TZ"
        kea = "kea"
        kea_CV = "kea_CV"
        khq = "khq"
        khq_ML = "khq_ML"
        ki = "ki"
        ki_KE = "ki_KE"
        kk = "kk"
        kk_Cyrl = "kk_Cyrl"
        kk_Cyrl_KZ = "kk_Cyrl_KZ"
        kl = "kl"
        kl_GL = "kl_GL"
        kln = "kln"
        kln_KE = "kln_KE"
        km = "km"
        km_KH = "km_KH"
        kn = "kn"
        kn_IN = "kn_IN"
        ko = "ko"
        ko_KP = "ko_KP"
        ko_KR = "ko_KR"
        kok = "kok"
        kok_IN = "kok_IN"
        ks = "ks"
        ks_Arab = "ks_Arab"
        ks_Arab_IN = "ks_Arab_IN"
        ksb = "ksb"
        ksb_TZ = "ksb_TZ"
        ksf = "ksf"
        ksf_CM = "ksf_CM"
        kw = "kw"
        kw_GB = "kw_GB"
        lag = "lag"
        lag_TZ = "lag_TZ"
        lg = "lg"
        lg_UG = "lg_UG"
        ln = "ln"
        ln_AO = "ln_AO"
        ln_CD = "ln_CD"
        ln_CF = "ln_CF"
        ln_CG = "ln_CG"
        lo = "lo"
        lo_LA = "lo_LA"
        lt = "lt"
        lt_LT = "lt_LT"
        lu = "lu"
        lu_CD = "lu_CD"
        luo = "luo"
        luo_KE = "luo_KE"
        luy = "luy"
        luy_KE = "luy_KE"
        lv = "lv"
        lv_LV = "lv_LV"
        mas = "mas"
        mas_KE = "mas_KE"
        mas_TZ = "mas_TZ"
        mer = "mer"
        mer_KE = "mer_KE"
        mfe = "mfe"
        mfe_MU = "mfe_MU"
        mg = "mg"
        mg_MG = "mg_MG"
        mgh = "mgh"
        mgh_MZ = "mgh_MZ"
        mgo = "mgo"
        mgo_CM = "mgo_CM"
        mk = "mk"
        mk_MK = "mk_MK"
        ml = "ml"
        ml_IN = "ml_IN"
        mr = "mr"
        mr_IN = "mr_IN"
        ms = "ms"
        ms_BN = "ms_BN"
        ms_MY = "ms_MY"
        ms_SG = "ms_SG"
        mt = "mt"
        mt_MT = "mt_MT"
        mua = "mua"
        mua_CM = "mua_CM"
        my = "my"
        my_MM = "my_MM"
        naq = "naq"
        naq_NA = "naq_NA"
        nb = "nb"
        nb_NO = "nb_NO"
        nd = "nd"
        nd_ZW = "nd_ZW"
        ne = "ne"
        ne_IN = "ne_IN"
        ne_NP = "ne_NP"
        nl = "nl"
        nl_AW = "nl_AW"
        nl_BE = "nl_BE"
        nl_CW = "nl_CW"
        nl_NL = "nl_NL"
        nl_SR = "nl_SR"
        nl_SX = "nl_SX"
        nmg = "nmg"
        nmg_CM = "nmg_CM"
        nn = "nn"
        nn_NO = "nn_NO"
        nus = "nus"
        nus_SD = "nus_SD"
        nyn = "nyn"
        nyn_UG = "nyn_UG"
        om = "om"
        om_ET = "om_ET"
        om_KE = "om_KE"
        or_ = "or"
        or_IN = "or_IN"
        pa = "pa"
        pa_Arab = "pa_Arab"
        pa_Arab_PK = "pa_Arab_PK"
        pa_Guru = "pa_Guru"
        pa_Guru_IN = "pa_Guru_IN"
        pl = "pl"
        pl_PL = "pl_PL"
        ps = "ps"
        ps_AF = "ps_AF"
        pt = "pt"
        pt_AO = "pt_AO"
        pt_BR = "pt_BR"
        pt_CV = "pt_CV"
        pt_GW = "pt_GW"
        pt_MO = "pt_MO"
        pt_MZ = "pt_MZ"
        pt_PT = "pt_PT"
        pt_ST = "pt_ST"
        pt_TL = "pt_TL"
        rm = "rm"
        rm_CH = "rm_CH"
        rn = "rn"
        rn_BI = "rn_BI"
        ro = "ro"
        ro_MD = "ro_MD"
        ro_RO = "ro_RO"
        rof = "rof"
        rof_TZ = "rof_TZ"
        ru = "ru"
        ru_BY = "ru_BY"
        ru_KG = "ru_KG"
        ru_KZ = "ru_KZ"
        ru_MD = "ru_MD"
        ru_RU = "ru_RU"
        ru_UA = "ru_UA"
        rw = "rw"
        rw_RW = "rw_RW"
        rwk = "rwk"
        rwk_TZ = "rwk_TZ"
        saq = "saq"
        saq_KE = "saq_KE"
        sbp = "sbp"
        sbp_TZ = "sbp_TZ"
        seh = "seh"
        seh_MZ = "seh_MZ"
        ses = "ses"
        ses_ML = "ses_ML"
        sg = "sg"
        sg_CF = "sg_CF"
        shi = "shi"
        shi_Latn = "shi_Latn"
        shi_Latn_MA = "shi_Latn_MA"
        shi_Tfng = "shi_Tfng"
        shi_Tfng_MA = "shi_Tfng_MA"
        si = "si"
        si_LK = "si_LK"
        sk = "sk"
        sk_SK = "sk_SK"
        sl = "sl"
        sl_SI = "sl_SI"
        sn = "sn"
        sn_ZW = "sn_ZW"
        so = "so"
        so_DJ = "so_DJ"
        so_ET = "so_ET"
        so_KE = "so_KE"
        so_SO = "so_SO"
        sq = "sq"
        sq_AL = "sq_AL"
        sq_MK = "sq_MK"
        sr = "sr"
        sr_Cyrl = "sr_Cyrl"
        sr_Cyrl_BA = "sr_Cyrl_BA"
        sr_Cyrl_ME = "sr_Cyrl_ME"
        sr_Cyrl_RS = "sr_Cyrl_RS"
        sr_Latn = "sr_Latn"
        sr_Latn_BA = "sr_Latn_BA"
        sr_Latn_ME = "sr_Latn_ME"
        sr_Latn_RS = "sr_Latn_RS"
        sv = "sv"
        sv_AX = "sv_AX"
        sv_FI = "sv_FI"
        sv_SE = "sv_SE"
        sw = "sw"
        sw_KE = "sw_KE"
        sw_TZ = "sw_TZ"
        sw_UG = "sw_UG"
        swc = "swc"
        swc_CD = "swc_CD"
        ta = "ta"
        ta_IN = "ta_IN"
        ta_LK = "ta_LK"
        ta_MY = "ta_MY"
        ta_SG = "ta_SG"
        te = "te"
        te_IN = "te_IN"
        teo = "teo"
        teo_KE = "teo_KE"
        teo_UG = "teo_UG"
        th = "th"
        th_TH = "th_TH"
        ti = "ti"
        ti_ER = "ti_ER"
        ti_ET = "ti_ET"
        to = "to"
        to_TO = "to_TO"
        tr = "tr"
        tr_CY = "tr_CY"
        tr_TR = "tr_TR"
        twq = "twq"
        twq_NE = "twq_NE"
        tzm = "tzm"
        tzm_Latn = "tzm_Latn"
        tzm_Latn_MA = "tzm_Latn_MA"
        uk = "uk"
        uk_UA = "uk_UA"
        ur = "ur"
        ur_IN = "ur_IN"
        ur_PK = "ur_PK"
        uz = "uz"
        uz_Arab = "uz_Arab"
        uz_Arab_AF = "uz_Arab_AF"
        uz_Cyrl = "uz_Cyrl"
        uz_Cyrl_UZ = "uz_Cyrl_UZ"
        uz_Latn = "uz_Latn"
        uz_Latn_UZ = "uz_Latn_UZ"
        vai = "vai"
        vai_Latn = "vai_Latn"
        vai_Latn_LR = "vai_Latn_LR"
        vai_Vaii = "vai_Vaii"
        vai_Vaii_LR = "vai_Vaii_LR"
        vi = "vi"
        vi_VN = "vi_VN"
        vun = "vun"
        vun_TZ = "vun_TZ"
        xog = "xog"
        xog_UG = "xog_UG"
        yav = "yav"
        yav_CM = "yav_CM"
        yo = "yo"
        yo_NG = "yo_NG"
        zh = "zh"
        zh_Hans = "zh_Hans"
        zh_Hans_CN = "zh_Hans_CN"
        zh_Hans_HK = "zh_Hans_HK"
        zh_Hans_MO = "zh_Hans_MO"
        zh_Hans_SG = "zh_Hans_SG"
        zh_Hant = "zh_Hant"
        zh_Hant_HK = "zh_Hant_HK"
        zh_Hant_MO = "zh_Hant_MO"
        zh_Hant_TW = "zh_Hant_TW"
        zu = "zu"
        zu_ZA = "zu_ZA"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class SORT:
    """Enums for properties in the SORT stage."""

    class Operator(Enum):
        """Enum for the Operator property."""

        psort_sorter_unix = "psort -sorter unix"
        tsort = "tsort"

    class Stats(Enum):
        """Enum for the Stats property."""

        true = "stats"
        false = " "

    class Stable(Enum):
        """Enum for the Stable property."""

        stable = "stable"
        nonStable = "nonStable"

    class Unique(Enum):
        """Enum for the Unique property."""

        false = " "
        true = "unique"

    class FlagCluster(Enum):
        """Enum for the FlagCluster property."""

        true = "flagCluster"
        false = " "

    class FlagKey(Enum):
        """Enum for the FlagKey property."""

        true = "flagKey"
        false = " "

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_set = -2
        clear = 0
        set = 1

    class CollationSequence(Enum):
        """Enum for the CollationSequence property."""

        OFF = "OFF"
        af = "af"
        af_NA = "af_NA"
        af_ZA = "af_ZA"
        agq = "agq"
        agq_CM = "agq_CM"
        ak = "ak"
        ak_GH = "ak_GH"
        am = "am"
        am_ET = "am_ET"
        ar = "ar"
        ar_001 = "ar_001"
        ar_AE = "ar_AE"
        ar_BH = "ar_BH"
        ar_DJ = "ar_DJ"
        ar_DZ = "ar_DZ"
        ar_EG = "ar_EG"
        ar_EH = "ar_EH"
        ar_ER = "ar_ER"
        ar_IL = "ar_IL"
        ar_IQ = "ar_IQ"
        ar_JO = "ar_JO"
        ar_KM = "ar_KM"
        ar_KW = "ar_KW"
        ar_LB = "ar_LB"
        ar_LY = "ar_LY"
        ar_MA = "ar_MA"
        ar_MR = "ar_MR"
        ar_OM = "ar_OM"
        ar_PS = "ar_PS"
        ar_QA = "ar_QA"
        ar_SA = "ar_SA"
        ar_SD = "ar_SD"
        ar_SO = "ar_SO"
        ar_SY = "ar_SY"
        ar_TD = "ar_TD"
        ar_TN = "ar_TN"
        ar_YE = "ar_YE"
        as_ = "as"
        as_IN = "as_IN"
        asa = "asa"
        asa_TZ = "asa_TZ"
        az = "az"
        az_Cyrl = "az_Cyrl"
        az_Cyrl_AZ = "az_Cyrl_AZ"
        az_Latn = "az_Latn"
        az_Latn_AZ = "az_Latn_AZ"
        bas = "bas"
        bas_CM = "bas_CM"
        be = "be"
        be_BY = "be_BY"
        bem = "bem"
        bem_ZM = "bem_ZM"
        bez = "bez"
        bez_TZ = "bez_TZ"
        bg = "bg"
        bg_BG = "bg_BG"
        bm = "bm"
        bm_ML = "bm_ML"
        bn = "bn"
        bn_BD = "bn_BD"
        bn_IN = "bn_IN"
        bo = "bo"
        bo_CN = "bo_CN"
        bo_IN = "bo_IN"
        br = "br"
        br_FR = "br_FR"
        brx = "brx"
        brx_IN = "brx_IN"
        bs = "bs"
        bs_Cyrl = "bs_Cyrl"
        bs_Cyrl_BA = "bs_Cyrl_BA"
        bs_Latn = "bs_Latn"
        bs_Latn_BA = "bs_Latn_BA"
        ca = "ca"
        ca_AD = "ca_AD"
        ca_ES = "ca_ES"
        cgg = "cgg"
        cgg_UG = "cgg_UG"
        chr = "chr"
        chr_US = "chr_US"
        cs = "cs"
        cs_CZ = "cs_CZ"
        cy = "cy"
        cy_GB = "cy_GB"
        da = "da"
        da_DK = "da_DK"
        dav = "dav"
        dav_KE = "dav_KE"
        de = "de"
        de_AT = "de_AT"
        de_BE = "de_BE"
        de_CH = "de_CH"
        de_DE = "de_DE"
        de_LI = "de_LI"
        de_LU = "de_LU"
        dje = "dje"
        dje_NE = "dje_NE"
        dua = "dua"
        dua_CM = "dua_CM"
        dyo = "dyo"
        dyo_SN = "dyo_SN"
        dz = "dz"
        dz_BT = "dz_BT"
        ebu = "ebu"
        ebu_KE = "ebu_KE"
        ee = "ee"
        ee_GH = "ee_GH"
        ee_TG = "ee_TG"
        el = "el"
        el_CY = "el_CY"
        el_GR = "el_GR"
        en = "en"
        en_150 = "en_150"
        en_AG = "en_AG"
        en_AS = "en_AS"
        en_AU = "en_AU"
        en_BB = "en_BB"
        en_BE = "en_BE"
        en_BM = "en_BM"
        en_BS = "en_BS"
        en_BW = "en_BW"
        en_BZ = "en_BZ"
        en_CA = "en_CA"
        en_CM = "en_CM"
        en_DM = "en_DM"
        en_FJ = "en_FJ"
        en_FM = "en_FM"
        en_GB = "en_GB"
        en_GD = "en_GD"
        en_GG = "en_GG"
        en_GH = "en_GH"
        en_GI = "en_GI"
        en_GM = "en_GM"
        en_GU = "en_GU"
        en_GY = "en_GY"
        en_HK = "en_HK"
        en_IE = "en_IE"
        en_IM = "en_IM"
        en_IN = "en_IN"
        en_JE = "en_JE"
        en_JM = "en_JM"
        en_KE = "en_KE"
        en_KI = "en_KI"
        en_KN = "en_KN"
        en_KY = "en_KY"
        en_LC = "en_LC"
        en_LR = "en_LR"
        en_LS = "en_LS"
        en_MG = "en_MG"
        en_MH = "en_MH"
        en_MP = "en_MP"
        en_MT = "en_MT"
        en_MU = "en_MU"
        en_MW = "en_MW"
        en_NA = "en_NA"
        en_NG = "en_NG"
        en_NZ = "en_NZ"
        en_PG = "en_PG"
        en_PH = "en_PH"
        en_PK = "en_PK"
        en_PR = "en_PR"
        en_PW = "en_PW"
        en_SB = "en_SB"
        en_SC = "en_SC"
        en_SG = "en_SG"
        en_SL = "en_SL"
        en_SS = "en_SS"
        en_SZ = "en_SZ"
        en_TC = "en_TC"
        en_TO = "en_TO"
        en_TT = "en_TT"
        en_TZ = "en_TZ"
        en_UG = "en_UG"
        en_UM = "en_UM"
        en_US = "en_US"
        en_US_POSIX = "en_US_POSIX"
        en_VC = "en_VC"
        en_VG = "en_VG"
        en_VI = "en_VI"
        en_VU = "en_VU"
        en_WS = "en_WS"
        en_ZA = "en_ZA"
        en_ZM = "en_ZM"
        en_ZW = "en_ZW"
        eo = "eo"
        es = "es"
        es_419 = "es_419"
        es_AR = "es_AR"
        es_BO = "es_BO"
        es_CL = "es_CL"
        es_CO = "es_CO"
        es_CR = "es_CR"
        es_CU = "es_CU"
        es_DO = "es_DO"
        es_EA = "es_EA"
        es_EC = "es_EC"
        es_ES = "es_ES"
        es_GQ = "es_GQ"
        es_GT = "es_GT"
        es_HN = "es_HN"
        es_IC = "es_IC"
        es_MX = "es_MX"
        es_NI = "es_NI"
        es_PA = "es_PA"
        es_PE = "es_PE"
        es_PH = "es_PH"
        es_PR = "es_PR"
        es_PY = "es_PY"
        es_SV = "es_SV"
        es_US = "es_US"
        es_UY = "es_UY"
        es_VE = "es_VE"
        et = "et"
        et_EE = "et_EE"
        eu = "eu"
        eu_ES = "eu_ES"
        ewo = "ewo"
        ewo_CM = "ewo_CM"
        fa = "fa"
        fa_AF = "fa_AF"
        fa_IR = "fa_IR"
        ff = "ff"
        ff_SN = "ff_SN"
        fi = "fi"
        fi_FI = "fi_FI"
        fil = "fil"
        fil_PH = "fil_PH"
        fo = "fo"
        fo_FO = "fo_FO"
        fr = "fr"
        fr_BE = "fr_BE"
        fr_BF = "fr_BF"
        fr_BI = "fr_BI"
        fr_BJ = "fr_BJ"
        fr_BL = "fr_BL"
        fr_CA = "fr_CA"
        fr_CD = "fr_CD"
        fr_CF = "fr_CF"
        fr_CG = "fr_CG"
        fr_CH = "fr_CH"
        fr_CI = "fr_CI"
        fr_CM = "fr_CM"
        fr_DJ = "fr_DJ"
        fr_DZ = "fr_DZ"
        fr_FR = "fr_FR"
        fr_GA = "fr_GA"
        fr_GF = "fr_GF"
        fr_GN = "fr_GN"
        fr_GP = "fr_GP"
        fr_GQ = "fr_GQ"
        fr_HT = "fr_HT"
        fr_KM = "fr_KM"
        fr_LU = "fr_LU"
        fr_MA = "fr_MA"
        fr_MC = "fr_MC"
        fr_MF = "fr_MF"
        fr_MG = "fr_MG"
        fr_ML = "fr_ML"
        fr_MQ = "fr_MQ"
        fr_MR = "fr_MR"
        fr_MU = "fr_MU"
        fr_NC = "fr_NC"
        fr_NE = "fr_NE"
        fr_PF = "fr_PF"
        fr_RE = "fr_RE"
        fr_RW = "fr_RW"
        fr_SC = "fr_SC"
        fr_SN = "fr_SN"
        fr_SY = "fr_SY"
        fr_TD = "fr_TD"
        fr_TG = "fr_TG"
        fr_TN = "fr_TN"
        fr_VU = "fr_VU"
        fr_YT = "fr_YT"
        ga = "ga"
        ga_IE = "ga_IE"
        gl = "gl"
        gl_ES = "gl_ES"
        gsw = "gsw"
        gsw_CH = "gsw_CH"
        gu = "gu"
        gu_IN = "gu_IN"
        guz = "guz"
        guz_KE = "guz_KE"
        gv = "gv"
        gv_GB = "gv_GB"
        ha = "ha"
        ha_Latn = "ha_Latn"
        ha_Latn_GH = "ha_Latn_GH"
        ha_Latn_NE = "ha_Latn_NE"
        ha_Latn_NG = "ha_Latn_NG"
        haw = "haw"
        haw_US = "haw_US"
        he = "he"
        he_IL = "he_IL"
        hi = "hi"
        hi_IN = "hi_IN"
        hr = "hr"
        hr_BA = "hr_BA"
        hr_HR = "hr_HR"
        hu = "hu"
        hu_HU = "hu_HU"
        hy = "hy"
        hy_AM = "hy_AM"
        id = "id"
        id_ID = "id_ID"
        ig = "ig"
        ig_NG = "ig_NG"
        ii = "ii"
        ii_CN = "ii_CN"
        is_ = "is"
        is_IS = "is_IS"
        it = "it"
        it_CH = "it_CH"
        it_IT = "it_IT"
        it_SM = "it_SM"
        ja = "ja"
        ja_JP = "ja_JP"
        jgo = "jgo"
        jgo_CM = "jgo_CM"
        jmc = "jmc"
        jmc_TZ = "jmc_TZ"
        ka = "ka"
        ka_GE = "ka_GE"
        kab = "kab"
        kab_DZ = "kab_DZ"
        kam = "kam"
        kam_KE = "kam_KE"
        kde = "kde"
        kde_TZ = "kde_TZ"
        kea = "kea"
        kea_CV = "kea_CV"
        khq = "khq"
        khq_ML = "khq_ML"
        ki = "ki"
        ki_KE = "ki_KE"
        kk = "kk"
        kk_Cyrl = "kk_Cyrl"
        kk_Cyrl_KZ = "kk_Cyrl_KZ"
        kl = "kl"
        kl_GL = "kl_GL"
        kln = "kln"
        kln_KE = "kln_KE"
        km = "km"
        km_KH = "km_KH"
        kn = "kn"
        kn_IN = "kn_IN"
        ko = "ko"
        ko_KP = "ko_KP"
        ko_KR = "ko_KR"
        kok = "kok"
        kok_IN = "kok_IN"
        ks = "ks"
        ks_Arab = "ks_Arab"
        ks_Arab_IN = "ks_Arab_IN"
        ksb = "ksb"
        ksb_TZ = "ksb_TZ"
        ksf = "ksf"
        ksf_CM = "ksf_CM"
        kw = "kw"
        kw_GB = "kw_GB"
        lag = "lag"
        lag_TZ = "lag_TZ"
        lg = "lg"
        lg_UG = "lg_UG"
        ln = "ln"
        ln_AO = "ln_AO"
        ln_CD = "ln_CD"
        ln_CF = "ln_CF"
        ln_CG = "ln_CG"
        lo = "lo"
        lo_LA = "lo_LA"
        lt = "lt"
        lt_LT = "lt_LT"
        lu = "lu"
        lu_CD = "lu_CD"
        luo = "luo"
        luo_KE = "luo_KE"
        luy = "luy"
        luy_KE = "luy_KE"
        lv = "lv"
        lv_LV = "lv_LV"
        mas = "mas"
        mas_KE = "mas_KE"
        mas_TZ = "mas_TZ"
        mer = "mer"
        mer_KE = "mer_KE"
        mfe = "mfe"
        mfe_MU = "mfe_MU"
        mg = "mg"
        mg_MG = "mg_MG"
        mgh = "mgh"
        mgh_MZ = "mgh_MZ"
        mgo = "mgo"
        mgo_CM = "mgo_CM"
        mk = "mk"
        mk_MK = "mk_MK"
        ml = "ml"
        ml_IN = "ml_IN"
        mr = "mr"
        mr_IN = "mr_IN"
        ms = "ms"
        ms_BN = "ms_BN"
        ms_MY = "ms_MY"
        ms_SG = "ms_SG"
        mt = "mt"
        mt_MT = "mt_MT"
        mua = "mua"
        mua_CM = "mua_CM"
        my = "my"
        my_MM = "my_MM"
        naq = "naq"
        naq_NA = "naq_NA"
        nb = "nb"
        nb_NO = "nb_NO"
        nd = "nd"
        nd_ZW = "nd_ZW"
        ne = "ne"
        ne_IN = "ne_IN"
        ne_NP = "ne_NP"
        nl = "nl"
        nl_AW = "nl_AW"
        nl_BE = "nl_BE"
        nl_CW = "nl_CW"
        nl_NL = "nl_NL"
        nl_SR = "nl_SR"
        nl_SX = "nl_SX"
        nmg = "nmg"
        nmg_CM = "nmg_CM"
        nn = "nn"
        nn_NO = "nn_NO"
        nus = "nus"
        nus_SD = "nus_SD"
        nyn = "nyn"
        nyn_UG = "nyn_UG"
        om = "om"
        om_ET = "om_ET"
        om_KE = "om_KE"
        or_ = "or"
        or_IN = "or_IN"
        pa = "pa"
        pa_Arab = "pa_Arab"
        pa_Arab_PK = "pa_Arab_PK"
        pa_Guru = "pa_Guru"
        pa_Guru_IN = "pa_Guru_IN"
        pl = "pl"
        pl_PL = "pl_PL"
        ps = "ps"
        ps_AF = "ps_AF"
        pt = "pt"
        pt_AO = "pt_AO"
        pt_BR = "pt_BR"
        pt_CV = "pt_CV"
        pt_GW = "pt_GW"
        pt_MO = "pt_MO"
        pt_MZ = "pt_MZ"
        pt_PT = "pt_PT"
        pt_ST = "pt_ST"
        pt_TL = "pt_TL"
        rm = "rm"
        rm_CH = "rm_CH"
        rn = "rn"
        rn_BI = "rn_BI"
        ro = "ro"
        ro_MD = "ro_MD"
        ro_RO = "ro_RO"
        rof = "rof"
        rof_TZ = "rof_TZ"
        ru = "ru"
        ru_BY = "ru_BY"
        ru_KG = "ru_KG"
        ru_KZ = "ru_KZ"
        ru_MD = "ru_MD"
        ru_RU = "ru_RU"
        ru_UA = "ru_UA"
        rw = "rw"
        rw_RW = "rw_RW"
        rwk = "rwk"
        rwk_TZ = "rwk_TZ"
        saq = "saq"
        saq_KE = "saq_KE"
        sbp = "sbp"
        sbp_TZ = "sbp_TZ"
        seh = "seh"
        seh_MZ = "seh_MZ"
        ses = "ses"
        ses_ML = "ses_ML"
        sg = "sg"
        sg_CF = "sg_CF"
        shi = "shi"
        shi_Latn = "shi_Latn"
        shi_Latn_MA = "shi_Latn_MA"
        shi_Tfng = "shi_Tfng"
        shi_Tfng_MA = "shi_Tfng_MA"
        si = "si"
        si_LK = "si_LK"
        sk = "sk"
        sk_SK = "sk_SK"
        sl = "sl"
        sl_SI = "sl_SI"
        sn = "sn"
        sn_ZW = "sn_ZW"
        so = "so"
        so_DJ = "so_DJ"
        so_ET = "so_ET"
        so_KE = "so_KE"
        so_SO = "so_SO"
        sq = "sq"
        sq_AL = "sq_AL"
        sq_MK = "sq_MK"
        sr = "sr"
        sr_Cyrl = "sr_Cyrl"
        sr_Cyrl_BA = "sr_Cyrl_BA"
        sr_Cyrl_ME = "sr_Cyrl_ME"
        sr_Cyrl_RS = "sr_Cyrl_RS"
        sr_Latn = "sr_Latn"
        sr_Latn_BA = "sr_Latn_BA"
        sr_Latn_ME = "sr_Latn_ME"
        sr_Latn_RS = "sr_Latn_RS"
        sv = "sv"
        sv_AX = "sv_AX"
        sv_FI = "sv_FI"
        sv_SE = "sv_SE"
        sw = "sw"
        sw_KE = "sw_KE"
        sw_TZ = "sw_TZ"
        sw_UG = "sw_UG"
        swc = "swc"
        swc_CD = "swc_CD"
        ta = "ta"
        ta_IN = "ta_IN"
        ta_LK = "ta_LK"
        ta_MY = "ta_MY"
        ta_SG = "ta_SG"
        te = "te"
        te_IN = "te_IN"
        teo = "teo"
        teo_KE = "teo_KE"
        teo_UG = "teo_UG"
        th = "th"
        th_TH = "th_TH"
        ti = "ti"
        ti_ER = "ti_ER"
        ti_ET = "ti_ET"
        to = "to"
        to_TO = "to_TO"
        tr = "tr"
        tr_CY = "tr_CY"
        tr_TR = "tr_TR"
        twq = "twq"
        twq_NE = "twq_NE"
        tzm = "tzm"
        tzm_Latn = "tzm_Latn"
        tzm_Latn_MA = "tzm_Latn_MA"
        uk = "uk"
        uk_UA = "uk_UA"
        ur = "ur"
        ur_IN = "ur_IN"
        ur_PK = "ur_PK"
        uz = "uz"
        uz_Arab = "uz_Arab"
        uz_Arab_AF = "uz_Arab_AF"
        uz_Cyrl = "uz_Cyrl"
        uz_Cyrl_UZ = "uz_Cyrl_UZ"
        uz_Latn = "uz_Latn"
        uz_Latn_UZ = "uz_Latn_UZ"
        vai = "vai"
        vai_Latn = "vai_Latn"
        vai_Latn_LR = "vai_Latn_LR"
        vai_Vaii = "vai_Vaii"
        vai_Vaii_LR = "vai_Vaii_LR"
        vi = "vi"
        vi_VN = "vi_VN"
        vun = "vun"
        vun_TZ = "vun_TZ"
        xog = "xog"
        xog_UG = "xog_UG"
        yav = "yav"
        yav_CM = "yav_CM"
        yo = "yo"
        yo_NG = "yo_NG"
        zh = "zh"
        zh_Hans = "zh_Hans"
        zh_Hans_CN = "zh_Hans_CN"
        zh_Hans_HK = "zh_Hans_HK"
        zh_Hans_MO = "zh_Hans_MO"
        zh_Hans_SG = "zh_Hans_SG"
        zh_Hant = "zh_Hant"
        zh_Hant_HK = "zh_Hant_HK"
        zh_Hant_MO = "zh_Hant_MO"
        zh_Hant_TW = "zh_Hant_TW"
        zu = "zu"
        zu_ZA = "zu_ZA"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class MAKE_VECTOR:
    """Enums for properties in the MAKE_VECTOR stage."""

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class FILTER:
    """Enums for properties in the FILTER stage."""

    class Reject(Enum):
        """Enum for the Reject property."""

        true = "reject"
        false = " "

    class Nulls(Enum):
        """Enum for the Nulls property."""

        last = "last"
        first = "first"

    class First(Enum):
        """Enum for the First property."""

        true = "first"
        false = " "

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class CollationSequence(Enum):
        """Enum for the CollationSequence property."""

        OFF = "OFF"
        af = "af"
        af_NA = "af_NA"
        af_ZA = "af_ZA"
        agq = "agq"
        agq_CM = "agq_CM"
        ak = "ak"
        ak_GH = "ak_GH"
        am = "am"
        am_ET = "am_ET"
        ar = "ar"
        ar_001 = "ar_001"
        ar_AE = "ar_AE"
        ar_BH = "ar_BH"
        ar_DJ = "ar_DJ"
        ar_DZ = "ar_DZ"
        ar_EG = "ar_EG"
        ar_EH = "ar_EH"
        ar_ER = "ar_ER"
        ar_IL = "ar_IL"
        ar_IQ = "ar_IQ"
        ar_JO = "ar_JO"
        ar_KM = "ar_KM"
        ar_KW = "ar_KW"
        ar_LB = "ar_LB"
        ar_LY = "ar_LY"
        ar_MA = "ar_MA"
        ar_MR = "ar_MR"
        ar_OM = "ar_OM"
        ar_PS = "ar_PS"
        ar_QA = "ar_QA"
        ar_SA = "ar_SA"
        ar_SD = "ar_SD"
        ar_SO = "ar_SO"
        ar_SY = "ar_SY"
        ar_TD = "ar_TD"
        ar_TN = "ar_TN"
        ar_YE = "ar_YE"
        as_ = "as"
        as_IN = "as_IN"
        asa = "asa"
        asa_TZ = "asa_TZ"
        az = "az"
        az_Cyrl = "az_Cyrl"
        az_Cyrl_AZ = "az_Cyrl_AZ"
        az_Latn = "az_Latn"
        az_Latn_AZ = "az_Latn_AZ"
        bas = "bas"
        bas_CM = "bas_CM"
        be = "be"
        be_BY = "be_BY"
        bem = "bem"
        bem_ZM = "bem_ZM"
        bez = "bez"
        bez_TZ = "bez_TZ"
        bg = "bg"
        bg_BG = "bg_BG"
        bm = "bm"
        bm_ML = "bm_ML"
        bn = "bn"
        bn_BD = "bn_BD"
        bn_IN = "bn_IN"
        bo = "bo"
        bo_CN = "bo_CN"
        bo_IN = "bo_IN"
        br = "br"
        br_FR = "br_FR"
        brx = "brx"
        brx_IN = "brx_IN"
        bs = "bs"
        bs_Cyrl = "bs_Cyrl"
        bs_Cyrl_BA = "bs_Cyrl_BA"
        bs_Latn = "bs_Latn"
        bs_Latn_BA = "bs_Latn_BA"
        ca = "ca"
        ca_AD = "ca_AD"
        ca_ES = "ca_ES"
        cgg = "cgg"
        cgg_UG = "cgg_UG"
        chr = "chr"
        chr_US = "chr_US"
        cs = "cs"
        cs_CZ = "cs_CZ"
        cy = "cy"
        cy_GB = "cy_GB"
        da = "da"
        da_DK = "da_DK"
        dav = "dav"
        dav_KE = "dav_KE"
        de = "de"
        de_AT = "de_AT"
        de_BE = "de_BE"
        de_CH = "de_CH"
        de_DE = "de_DE"
        de_LI = "de_LI"
        de_LU = "de_LU"
        dje = "dje"
        dje_NE = "dje_NE"
        dua = "dua"
        dua_CM = "dua_CM"
        dyo = "dyo"
        dyo_SN = "dyo_SN"
        dz = "dz"
        dz_BT = "dz_BT"
        ebu = "ebu"
        ebu_KE = "ebu_KE"
        ee = "ee"
        ee_GH = "ee_GH"
        ee_TG = "ee_TG"
        el = "el"
        el_CY = "el_CY"
        el_GR = "el_GR"
        en = "en"
        en_150 = "en_150"
        en_AG = "en_AG"
        en_AS = "en_AS"
        en_AU = "en_AU"
        en_BB = "en_BB"
        en_BE = "en_BE"
        en_BM = "en_BM"
        en_BS = "en_BS"
        en_BW = "en_BW"
        en_BZ = "en_BZ"
        en_CA = "en_CA"
        en_CM = "en_CM"
        en_DM = "en_DM"
        en_FJ = "en_FJ"
        en_FM = "en_FM"
        en_GB = "en_GB"
        en_GD = "en_GD"
        en_GG = "en_GG"
        en_GH = "en_GH"
        en_GI = "en_GI"
        en_GM = "en_GM"
        en_GU = "en_GU"
        en_GY = "en_GY"
        en_HK = "en_HK"
        en_IE = "en_IE"
        en_IM = "en_IM"
        en_IN = "en_IN"
        en_JE = "en_JE"
        en_JM = "en_JM"
        en_KE = "en_KE"
        en_KI = "en_KI"
        en_KN = "en_KN"
        en_KY = "en_KY"
        en_LC = "en_LC"
        en_LR = "en_LR"
        en_LS = "en_LS"
        en_MG = "en_MG"
        en_MH = "en_MH"
        en_MP = "en_MP"
        en_MT = "en_MT"
        en_MU = "en_MU"
        en_MW = "en_MW"
        en_NA = "en_NA"
        en_NG = "en_NG"
        en_NZ = "en_NZ"
        en_PG = "en_PG"
        en_PH = "en_PH"
        en_PK = "en_PK"
        en_PR = "en_PR"
        en_PW = "en_PW"
        en_SB = "en_SB"
        en_SC = "en_SC"
        en_SG = "en_SG"
        en_SL = "en_SL"
        en_SS = "en_SS"
        en_SZ = "en_SZ"
        en_TC = "en_TC"
        en_TO = "en_TO"
        en_TT = "en_TT"
        en_TZ = "en_TZ"
        en_UG = "en_UG"
        en_UM = "en_UM"
        en_US = "en_US"
        en_US_POSIX = "en_US_POSIX"
        en_VC = "en_VC"
        en_VG = "en_VG"
        en_VI = "en_VI"
        en_VU = "en_VU"
        en_WS = "en_WS"
        en_ZA = "en_ZA"
        en_ZM = "en_ZM"
        en_ZW = "en_ZW"
        eo = "eo"
        es = "es"
        es_419 = "es_419"
        es_AR = "es_AR"
        es_BO = "es_BO"
        es_CL = "es_CL"
        es_CO = "es_CO"
        es_CR = "es_CR"
        es_CU = "es_CU"
        es_DO = "es_DO"
        es_EA = "es_EA"
        es_EC = "es_EC"
        es_ES = "es_ES"
        es_GQ = "es_GQ"
        es_GT = "es_GT"
        es_HN = "es_HN"
        es_IC = "es_IC"
        es_MX = "es_MX"
        es_NI = "es_NI"
        es_PA = "es_PA"
        es_PE = "es_PE"
        es_PH = "es_PH"
        es_PR = "es_PR"
        es_PY = "es_PY"
        es_SV = "es_SV"
        es_US = "es_US"
        es_UY = "es_UY"
        es_VE = "es_VE"
        et = "et"
        et_EE = "et_EE"
        eu = "eu"
        eu_ES = "eu_ES"
        ewo = "ewo"
        ewo_CM = "ewo_CM"
        fa = "fa"
        fa_AF = "fa_AF"
        fa_IR = "fa_IR"
        ff = "ff"
        ff_SN = "ff_SN"
        fi = "fi"
        fi_FI = "fi_FI"
        fil = "fil"
        fil_PH = "fil_PH"
        fo = "fo"
        fo_FO = "fo_FO"
        fr = "fr"
        fr_BE = "fr_BE"
        fr_BF = "fr_BF"
        fr_BI = "fr_BI"
        fr_BJ = "fr_BJ"
        fr_BL = "fr_BL"
        fr_CA = "fr_CA"
        fr_CD = "fr_CD"
        fr_CF = "fr_CF"
        fr_CG = "fr_CG"
        fr_CH = "fr_CH"
        fr_CI = "fr_CI"
        fr_CM = "fr_CM"
        fr_DJ = "fr_DJ"
        fr_DZ = "fr_DZ"
        fr_FR = "fr_FR"
        fr_GA = "fr_GA"
        fr_GF = "fr_GF"
        fr_GN = "fr_GN"
        fr_GP = "fr_GP"
        fr_GQ = "fr_GQ"
        fr_HT = "fr_HT"
        fr_KM = "fr_KM"
        fr_LU = "fr_LU"
        fr_MA = "fr_MA"
        fr_MC = "fr_MC"
        fr_MF = "fr_MF"
        fr_MG = "fr_MG"
        fr_ML = "fr_ML"
        fr_MQ = "fr_MQ"
        fr_MR = "fr_MR"
        fr_MU = "fr_MU"
        fr_NC = "fr_NC"
        fr_NE = "fr_NE"
        fr_PF = "fr_PF"
        fr_RE = "fr_RE"
        fr_RW = "fr_RW"
        fr_SC = "fr_SC"
        fr_SN = "fr_SN"
        fr_SY = "fr_SY"
        fr_TD = "fr_TD"
        fr_TG = "fr_TG"
        fr_TN = "fr_TN"
        fr_VU = "fr_VU"
        fr_YT = "fr_YT"
        ga = "ga"
        ga_IE = "ga_IE"
        gl = "gl"
        gl_ES = "gl_ES"
        gsw = "gsw"
        gsw_CH = "gsw_CH"
        gu = "gu"
        gu_IN = "gu_IN"
        guz = "guz"
        guz_KE = "guz_KE"
        gv = "gv"
        gv_GB = "gv_GB"
        ha = "ha"
        ha_Latn = "ha_Latn"
        ha_Latn_GH = "ha_Latn_GH"
        ha_Latn_NE = "ha_Latn_NE"
        ha_Latn_NG = "ha_Latn_NG"
        haw = "haw"
        haw_US = "haw_US"
        he = "he"
        he_IL = "he_IL"
        hi = "hi"
        hi_IN = "hi_IN"
        hr = "hr"
        hr_BA = "hr_BA"
        hr_HR = "hr_HR"
        hu = "hu"
        hu_HU = "hu_HU"
        hy = "hy"
        hy_AM = "hy_AM"
        id = "id"
        id_ID = "id_ID"
        ig = "ig"
        ig_NG = "ig_NG"
        ii = "ii"
        ii_CN = "ii_CN"
        is_ = "is"
        is_IS = "is_IS"
        it = "it"
        it_CH = "it_CH"
        it_IT = "it_IT"
        it_SM = "it_SM"
        ja = "ja"
        ja_JP = "ja_JP"
        jgo = "jgo"
        jgo_CM = "jgo_CM"
        jmc = "jmc"
        jmc_TZ = "jmc_TZ"
        ka = "ka"
        ka_GE = "ka_GE"
        kab = "kab"
        kab_DZ = "kab_DZ"
        kam = "kam"
        kam_KE = "kam_KE"
        kde = "kde"
        kde_TZ = "kde_TZ"
        kea = "kea"
        kea_CV = "kea_CV"
        khq = "khq"
        khq_ML = "khq_ML"
        ki = "ki"
        ki_KE = "ki_KE"
        kk = "kk"
        kk_Cyrl = "kk_Cyrl"
        kk_Cyrl_KZ = "kk_Cyrl_KZ"
        kl = "kl"
        kl_GL = "kl_GL"
        kln = "kln"
        kln_KE = "kln_KE"
        km = "km"
        km_KH = "km_KH"
        kn = "kn"
        kn_IN = "kn_IN"
        ko = "ko"
        ko_KP = "ko_KP"
        ko_KR = "ko_KR"
        kok = "kok"
        kok_IN = "kok_IN"
        ks = "ks"
        ks_Arab = "ks_Arab"
        ks_Arab_IN = "ks_Arab_IN"
        ksb = "ksb"
        ksb_TZ = "ksb_TZ"
        ksf = "ksf"
        ksf_CM = "ksf_CM"
        kw = "kw"
        kw_GB = "kw_GB"
        lag = "lag"
        lag_TZ = "lag_TZ"
        lg = "lg"
        lg_UG = "lg_UG"
        ln = "ln"
        ln_AO = "ln_AO"
        ln_CD = "ln_CD"
        ln_CF = "ln_CF"
        ln_CG = "ln_CG"
        lo = "lo"
        lo_LA = "lo_LA"
        lt = "lt"
        lt_LT = "lt_LT"
        lu = "lu"
        lu_CD = "lu_CD"
        luo = "luo"
        luo_KE = "luo_KE"
        luy = "luy"
        luy_KE = "luy_KE"
        lv = "lv"
        lv_LV = "lv_LV"
        mas = "mas"
        mas_KE = "mas_KE"
        mas_TZ = "mas_TZ"
        mer = "mer"
        mer_KE = "mer_KE"
        mfe = "mfe"
        mfe_MU = "mfe_MU"
        mg = "mg"
        mg_MG = "mg_MG"
        mgh = "mgh"
        mgh_MZ = "mgh_MZ"
        mgo = "mgo"
        mgo_CM = "mgo_CM"
        mk = "mk"
        mk_MK = "mk_MK"
        ml = "ml"
        ml_IN = "ml_IN"
        mr = "mr"
        mr_IN = "mr_IN"
        ms = "ms"
        ms_BN = "ms_BN"
        ms_MY = "ms_MY"
        ms_SG = "ms_SG"
        mt = "mt"
        mt_MT = "mt_MT"
        mua = "mua"
        mua_CM = "mua_CM"
        my = "my"
        my_MM = "my_MM"
        naq = "naq"
        naq_NA = "naq_NA"
        nb = "nb"
        nb_NO = "nb_NO"
        nd = "nd"
        nd_ZW = "nd_ZW"
        ne = "ne"
        ne_IN = "ne_IN"
        ne_NP = "ne_NP"
        nl = "nl"
        nl_AW = "nl_AW"
        nl_BE = "nl_BE"
        nl_CW = "nl_CW"
        nl_NL = "nl_NL"
        nl_SR = "nl_SR"
        nl_SX = "nl_SX"
        nmg = "nmg"
        nmg_CM = "nmg_CM"
        nn = "nn"
        nn_NO = "nn_NO"
        nus = "nus"
        nus_SD = "nus_SD"
        nyn = "nyn"
        nyn_UG = "nyn_UG"
        om = "om"
        om_ET = "om_ET"
        om_KE = "om_KE"
        or_ = "or"
        or_IN = "or_IN"
        pa = "pa"
        pa_Arab = "pa_Arab"
        pa_Arab_PK = "pa_Arab_PK"
        pa_Guru = "pa_Guru"
        pa_Guru_IN = "pa_Guru_IN"
        pl = "pl"
        pl_PL = "pl_PL"
        ps = "ps"
        ps_AF = "ps_AF"
        pt = "pt"
        pt_AO = "pt_AO"
        pt_BR = "pt_BR"
        pt_CV = "pt_CV"
        pt_GW = "pt_GW"
        pt_MO = "pt_MO"
        pt_MZ = "pt_MZ"
        pt_PT = "pt_PT"
        pt_ST = "pt_ST"
        pt_TL = "pt_TL"
        rm = "rm"
        rm_CH = "rm_CH"
        rn = "rn"
        rn_BI = "rn_BI"
        ro = "ro"
        ro_MD = "ro_MD"
        ro_RO = "ro_RO"
        rof = "rof"
        rof_TZ = "rof_TZ"
        ru = "ru"
        ru_BY = "ru_BY"
        ru_KG = "ru_KG"
        ru_KZ = "ru_KZ"
        ru_MD = "ru_MD"
        ru_RU = "ru_RU"
        ru_UA = "ru_UA"
        rw = "rw"
        rw_RW = "rw_RW"
        rwk = "rwk"
        rwk_TZ = "rwk_TZ"
        saq = "saq"
        saq_KE = "saq_KE"
        sbp = "sbp"
        sbp_TZ = "sbp_TZ"
        seh = "seh"
        seh_MZ = "seh_MZ"
        ses = "ses"
        ses_ML = "ses_ML"
        sg = "sg"
        sg_CF = "sg_CF"
        shi = "shi"
        shi_Latn = "shi_Latn"
        shi_Latn_MA = "shi_Latn_MA"
        shi_Tfng = "shi_Tfng"
        shi_Tfng_MA = "shi_Tfng_MA"
        si = "si"
        si_LK = "si_LK"
        sk = "sk"
        sk_SK = "sk_SK"
        sl = "sl"
        sl_SI = "sl_SI"
        sn = "sn"
        sn_ZW = "sn_ZW"
        so = "so"
        so_DJ = "so_DJ"
        so_ET = "so_ET"
        so_KE = "so_KE"
        so_SO = "so_SO"
        sq = "sq"
        sq_AL = "sq_AL"
        sq_MK = "sq_MK"
        sr = "sr"
        sr_Cyrl = "sr_Cyrl"
        sr_Cyrl_BA = "sr_Cyrl_BA"
        sr_Cyrl_ME = "sr_Cyrl_ME"
        sr_Cyrl_RS = "sr_Cyrl_RS"
        sr_Latn = "sr_Latn"
        sr_Latn_BA = "sr_Latn_BA"
        sr_Latn_ME = "sr_Latn_ME"
        sr_Latn_RS = "sr_Latn_RS"
        sv = "sv"
        sv_AX = "sv_AX"
        sv_FI = "sv_FI"
        sv_SE = "sv_SE"
        sw = "sw"
        sw_KE = "sw_KE"
        sw_TZ = "sw_TZ"
        sw_UG = "sw_UG"
        swc = "swc"
        swc_CD = "swc_CD"
        ta = "ta"
        ta_IN = "ta_IN"
        ta_LK = "ta_LK"
        ta_MY = "ta_MY"
        ta_SG = "ta_SG"
        te = "te"
        te_IN = "te_IN"
        teo = "teo"
        teo_KE = "teo_KE"
        teo_UG = "teo_UG"
        th = "th"
        th_TH = "th_TH"
        ti = "ti"
        ti_ER = "ti_ER"
        ti_ET = "ti_ET"
        to = "to"
        to_TO = "to_TO"
        tr = "tr"
        tr_CY = "tr_CY"
        tr_TR = "tr_TR"
        twq = "twq"
        twq_NE = "twq_NE"
        tzm = "tzm"
        tzm_Latn = "tzm_Latn"
        tzm_Latn_MA = "tzm_Latn_MA"
        uk = "uk"
        uk_UA = "uk_UA"
        ur = "ur"
        ur_IN = "ur_IN"
        ur_PK = "ur_PK"
        uz = "uz"
        uz_Arab = "uz_Arab"
        uz_Arab_AF = "uz_Arab_AF"
        uz_Cyrl = "uz_Cyrl"
        uz_Cyrl_UZ = "uz_Cyrl_UZ"
        uz_Latn = "uz_Latn"
        uz_Latn_UZ = "uz_Latn_UZ"
        vai = "vai"
        vai_Latn = "vai_Latn"
        vai_Latn_LR = "vai_Latn_LR"
        vai_Vaii = "vai_Vaii"
        vai_Vaii_LR = "vai_Vaii_LR"
        vi = "vi"
        vi_VN = "vi_VN"
        vun = "vun"
        vun_TZ = "vun_TZ"
        xog = "xog"
        xog_UG = "xog_UG"
        yav = "yav"
        yav_CM = "yav_CM"
        yo = "yo"
        yo_NG = "yo_NG"
        zh = "zh"
        zh_Hans = "zh_Hans"
        zh_Hans_CN = "zh_Hans_CN"
        zh_Hans_HK = "zh_Hans_HK"
        zh_Hans_MO = "zh_Hans_MO"
        zh_Hans_SG = "zh_Hans_SG"
        zh_Hant = "zh_Hant"
        zh_Hant_HK = "zh_Hant_HK"
        zh_Hant_MO = "zh_Hant_MO"
        zh_Hant_TW = "zh_Hant_TW"
        zu = "zu"
        zu_ZA = "zu_ZA"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class PROMOTE_SUBRECORD:
    """Enums for properties in the PROMOTE_SUBRECORD stage."""

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class INVESTIGATE:
    """Enums for properties in the INVESTIGATE stage."""

    class Word(Enum):
        """Enum for the Word property."""

        false = " "
        true = "word"

    class TokenEdit(Enum):
        """Enum for the TokenEdit property."""

        abbrev = "abbrev"
        original = "original"
        correct = "correct"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        db2part = "db2part"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class Db2NameSelect(Enum):
        """Enum for the Db2NameSelect property."""

        use_db2NameEnv = "use_db2NameEnv"
        use_userDefinedName = "use_userDefinedName"

    class Db2InstanceSelect(Enum):
        """Enum for the Db2InstanceSelect property."""

        use_db2InstanceEnv = "use_db2InstanceEnv"
        use_userDefinedInstance = "use_userDefinedInstance"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        Select_a_column = "Select a column"


class REMOVE_DUPLICATES:
    """Enums for properties in the REMOVE_DUPLICATES stage."""

    class Keep(Enum):
        """Enum for the Keep property."""

        first = "first"
        last = "last"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class CollationSequence(Enum):
        """Enum for the CollationSequence property."""

        OFF = "OFF"
        af = "af"
        af_NA = "af_NA"
        af_ZA = "af_ZA"
        agq = "agq"
        agq_CM = "agq_CM"
        ak = "ak"
        ak_GH = "ak_GH"
        am = "am"
        am_ET = "am_ET"
        ar = "ar"
        ar_001 = "ar_001"
        ar_AE = "ar_AE"
        ar_BH = "ar_BH"
        ar_DJ = "ar_DJ"
        ar_DZ = "ar_DZ"
        ar_EG = "ar_EG"
        ar_EH = "ar_EH"
        ar_ER = "ar_ER"
        ar_IL = "ar_IL"
        ar_IQ = "ar_IQ"
        ar_JO = "ar_JO"
        ar_KM = "ar_KM"
        ar_KW = "ar_KW"
        ar_LB = "ar_LB"
        ar_LY = "ar_LY"
        ar_MA = "ar_MA"
        ar_MR = "ar_MR"
        ar_OM = "ar_OM"
        ar_PS = "ar_PS"
        ar_QA = "ar_QA"
        ar_SA = "ar_SA"
        ar_SD = "ar_SD"
        ar_SO = "ar_SO"
        ar_SY = "ar_SY"
        ar_TD = "ar_TD"
        ar_TN = "ar_TN"
        ar_YE = "ar_YE"
        as_ = "as"
        as_IN = "as_IN"
        asa = "asa"
        asa_TZ = "asa_TZ"
        az = "az"
        az_Cyrl = "az_Cyrl"
        az_Cyrl_AZ = "az_Cyrl_AZ"
        az_Latn = "az_Latn"
        az_Latn_AZ = "az_Latn_AZ"
        bas = "bas"
        bas_CM = "bas_CM"
        be = "be"
        be_BY = "be_BY"
        bem = "bem"
        bem_ZM = "bem_ZM"
        bez = "bez"
        bez_TZ = "bez_TZ"
        bg = "bg"
        bg_BG = "bg_BG"
        bm = "bm"
        bm_ML = "bm_ML"
        bn = "bn"
        bn_BD = "bn_BD"
        bn_IN = "bn_IN"
        bo = "bo"
        bo_CN = "bo_CN"
        bo_IN = "bo_IN"
        br = "br"
        br_FR = "br_FR"
        brx = "brx"
        brx_IN = "brx_IN"
        bs = "bs"
        bs_Cyrl = "bs_Cyrl"
        bs_Cyrl_BA = "bs_Cyrl_BA"
        bs_Latn = "bs_Latn"
        bs_Latn_BA = "bs_Latn_BA"
        ca = "ca"
        ca_AD = "ca_AD"
        ca_ES = "ca_ES"
        cgg = "cgg"
        cgg_UG = "cgg_UG"
        chr = "chr"
        chr_US = "chr_US"
        cs = "cs"
        cs_CZ = "cs_CZ"
        cy = "cy"
        cy_GB = "cy_GB"
        da = "da"
        da_DK = "da_DK"
        dav = "dav"
        dav_KE = "dav_KE"
        de = "de"
        de_AT = "de_AT"
        de_BE = "de_BE"
        de_CH = "de_CH"
        de_DE = "de_DE"
        de_LI = "de_LI"
        de_LU = "de_LU"
        dje = "dje"
        dje_NE = "dje_NE"
        dua = "dua"
        dua_CM = "dua_CM"
        dyo = "dyo"
        dyo_SN = "dyo_SN"
        dz = "dz"
        dz_BT = "dz_BT"
        ebu = "ebu"
        ebu_KE = "ebu_KE"
        ee = "ee"
        ee_GH = "ee_GH"
        ee_TG = "ee_TG"
        el = "el"
        el_CY = "el_CY"
        el_GR = "el_GR"
        en = "en"
        en_150 = "en_150"
        en_AG = "en_AG"
        en_AS = "en_AS"
        en_AU = "en_AU"
        en_BB = "en_BB"
        en_BE = "en_BE"
        en_BM = "en_BM"
        en_BS = "en_BS"
        en_BW = "en_BW"
        en_BZ = "en_BZ"
        en_CA = "en_CA"
        en_CM = "en_CM"
        en_DM = "en_DM"
        en_FJ = "en_FJ"
        en_FM = "en_FM"
        en_GB = "en_GB"
        en_GD = "en_GD"
        en_GG = "en_GG"
        en_GH = "en_GH"
        en_GI = "en_GI"
        en_GM = "en_GM"
        en_GU = "en_GU"
        en_GY = "en_GY"
        en_HK = "en_HK"
        en_IE = "en_IE"
        en_IM = "en_IM"
        en_IN = "en_IN"
        en_JE = "en_JE"
        en_JM = "en_JM"
        en_KE = "en_KE"
        en_KI = "en_KI"
        en_KN = "en_KN"
        en_KY = "en_KY"
        en_LC = "en_LC"
        en_LR = "en_LR"
        en_LS = "en_LS"
        en_MG = "en_MG"
        en_MH = "en_MH"
        en_MP = "en_MP"
        en_MT = "en_MT"
        en_MU = "en_MU"
        en_MW = "en_MW"
        en_NA = "en_NA"
        en_NG = "en_NG"
        en_NZ = "en_NZ"
        en_PG = "en_PG"
        en_PH = "en_PH"
        en_PK = "en_PK"
        en_PR = "en_PR"
        en_PW = "en_PW"
        en_SB = "en_SB"
        en_SC = "en_SC"
        en_SG = "en_SG"
        en_SL = "en_SL"
        en_SS = "en_SS"
        en_SZ = "en_SZ"
        en_TC = "en_TC"
        en_TO = "en_TO"
        en_TT = "en_TT"
        en_TZ = "en_TZ"
        en_UG = "en_UG"
        en_UM = "en_UM"
        en_US = "en_US"
        en_US_POSIX = "en_US_POSIX"
        en_VC = "en_VC"
        en_VG = "en_VG"
        en_VI = "en_VI"
        en_VU = "en_VU"
        en_WS = "en_WS"
        en_ZA = "en_ZA"
        en_ZM = "en_ZM"
        en_ZW = "en_ZW"
        eo = "eo"
        es = "es"
        es_419 = "es_419"
        es_AR = "es_AR"
        es_BO = "es_BO"
        es_CL = "es_CL"
        es_CO = "es_CO"
        es_CR = "es_CR"
        es_CU = "es_CU"
        es_DO = "es_DO"
        es_EA = "es_EA"
        es_EC = "es_EC"
        es_ES = "es_ES"
        es_GQ = "es_GQ"
        es_GT = "es_GT"
        es_HN = "es_HN"
        es_IC = "es_IC"
        es_MX = "es_MX"
        es_NI = "es_NI"
        es_PA = "es_PA"
        es_PE = "es_PE"
        es_PH = "es_PH"
        es_PR = "es_PR"
        es_PY = "es_PY"
        es_SV = "es_SV"
        es_US = "es_US"
        es_UY = "es_UY"
        es_VE = "es_VE"
        et = "et"
        et_EE = "et_EE"
        eu = "eu"
        eu_ES = "eu_ES"
        ewo = "ewo"
        ewo_CM = "ewo_CM"
        fa = "fa"
        fa_AF = "fa_AF"
        fa_IR = "fa_IR"
        ff = "ff"
        ff_SN = "ff_SN"
        fi = "fi"
        fi_FI = "fi_FI"
        fil = "fil"
        fil_PH = "fil_PH"
        fo = "fo"
        fo_FO = "fo_FO"
        fr = "fr"
        fr_BE = "fr_BE"
        fr_BF = "fr_BF"
        fr_BI = "fr_BI"
        fr_BJ = "fr_BJ"
        fr_BL = "fr_BL"
        fr_CA = "fr_CA"
        fr_CD = "fr_CD"
        fr_CF = "fr_CF"
        fr_CG = "fr_CG"
        fr_CH = "fr_CH"
        fr_CI = "fr_CI"
        fr_CM = "fr_CM"
        fr_DJ = "fr_DJ"
        fr_DZ = "fr_DZ"
        fr_FR = "fr_FR"
        fr_GA = "fr_GA"
        fr_GF = "fr_GF"
        fr_GN = "fr_GN"
        fr_GP = "fr_GP"
        fr_GQ = "fr_GQ"
        fr_HT = "fr_HT"
        fr_KM = "fr_KM"
        fr_LU = "fr_LU"
        fr_MA = "fr_MA"
        fr_MC = "fr_MC"
        fr_MF = "fr_MF"
        fr_MG = "fr_MG"
        fr_ML = "fr_ML"
        fr_MQ = "fr_MQ"
        fr_MR = "fr_MR"
        fr_MU = "fr_MU"
        fr_NC = "fr_NC"
        fr_NE = "fr_NE"
        fr_PF = "fr_PF"
        fr_RE = "fr_RE"
        fr_RW = "fr_RW"
        fr_SC = "fr_SC"
        fr_SN = "fr_SN"
        fr_SY = "fr_SY"
        fr_TD = "fr_TD"
        fr_TG = "fr_TG"
        fr_TN = "fr_TN"
        fr_VU = "fr_VU"
        fr_YT = "fr_YT"
        ga = "ga"
        ga_IE = "ga_IE"
        gl = "gl"
        gl_ES = "gl_ES"
        gsw = "gsw"
        gsw_CH = "gsw_CH"
        gu = "gu"
        gu_IN = "gu_IN"
        guz = "guz"
        guz_KE = "guz_KE"
        gv = "gv"
        gv_GB = "gv_GB"
        ha = "ha"
        ha_Latn = "ha_Latn"
        ha_Latn_GH = "ha_Latn_GH"
        ha_Latn_NE = "ha_Latn_NE"
        ha_Latn_NG = "ha_Latn_NG"
        haw = "haw"
        haw_US = "haw_US"
        he = "he"
        he_IL = "he_IL"
        hi = "hi"
        hi_IN = "hi_IN"
        hr = "hr"
        hr_BA = "hr_BA"
        hr_HR = "hr_HR"
        hu = "hu"
        hu_HU = "hu_HU"
        hy = "hy"
        hy_AM = "hy_AM"
        id = "id"
        id_ID = "id_ID"
        ig = "ig"
        ig_NG = "ig_NG"
        ii = "ii"
        ii_CN = "ii_CN"
        is_ = "is"
        is_IS = "is_IS"
        it = "it"
        it_CH = "it_CH"
        it_IT = "it_IT"
        it_SM = "it_SM"
        ja = "ja"
        ja_JP = "ja_JP"
        jgo = "jgo"
        jgo_CM = "jgo_CM"
        jmc = "jmc"
        jmc_TZ = "jmc_TZ"
        ka = "ka"
        ka_GE = "ka_GE"
        kab = "kab"
        kab_DZ = "kab_DZ"
        kam = "kam"
        kam_KE = "kam_KE"
        kde = "kde"
        kde_TZ = "kde_TZ"
        kea = "kea"
        kea_CV = "kea_CV"
        khq = "khq"
        khq_ML = "khq_ML"
        ki = "ki"
        ki_KE = "ki_KE"
        kk = "kk"
        kk_Cyrl = "kk_Cyrl"
        kk_Cyrl_KZ = "kk_Cyrl_KZ"
        kl = "kl"
        kl_GL = "kl_GL"
        kln = "kln"
        kln_KE = "kln_KE"
        km = "km"
        km_KH = "km_KH"
        kn = "kn"
        kn_IN = "kn_IN"
        ko = "ko"
        ko_KP = "ko_KP"
        ko_KR = "ko_KR"
        kok = "kok"
        kok_IN = "kok_IN"
        ks = "ks"
        ks_Arab = "ks_Arab"
        ks_Arab_IN = "ks_Arab_IN"
        ksb = "ksb"
        ksb_TZ = "ksb_TZ"
        ksf = "ksf"
        ksf_CM = "ksf_CM"
        kw = "kw"
        kw_GB = "kw_GB"
        lag = "lag"
        lag_TZ = "lag_TZ"
        lg = "lg"
        lg_UG = "lg_UG"
        ln = "ln"
        ln_AO = "ln_AO"
        ln_CD = "ln_CD"
        ln_CF = "ln_CF"
        ln_CG = "ln_CG"
        lo = "lo"
        lo_LA = "lo_LA"
        lt = "lt"
        lt_LT = "lt_LT"
        lu = "lu"
        lu_CD = "lu_CD"
        luo = "luo"
        luo_KE = "luo_KE"
        luy = "luy"
        luy_KE = "luy_KE"
        lv = "lv"
        lv_LV = "lv_LV"
        mas = "mas"
        mas_KE = "mas_KE"
        mas_TZ = "mas_TZ"
        mer = "mer"
        mer_KE = "mer_KE"
        mfe = "mfe"
        mfe_MU = "mfe_MU"
        mg = "mg"
        mg_MG = "mg_MG"
        mgh = "mgh"
        mgh_MZ = "mgh_MZ"
        mgo = "mgo"
        mgo_CM = "mgo_CM"
        mk = "mk"
        mk_MK = "mk_MK"
        ml = "ml"
        ml_IN = "ml_IN"
        mr = "mr"
        mr_IN = "mr_IN"
        ms = "ms"
        ms_BN = "ms_BN"
        ms_MY = "ms_MY"
        ms_SG = "ms_SG"
        mt = "mt"
        mt_MT = "mt_MT"
        mua = "mua"
        mua_CM = "mua_CM"
        my = "my"
        my_MM = "my_MM"
        naq = "naq"
        naq_NA = "naq_NA"
        nb = "nb"
        nb_NO = "nb_NO"
        nd = "nd"
        nd_ZW = "nd_ZW"
        ne = "ne"
        ne_IN = "ne_IN"
        ne_NP = "ne_NP"
        nl = "nl"
        nl_AW = "nl_AW"
        nl_BE = "nl_BE"
        nl_CW = "nl_CW"
        nl_NL = "nl_NL"
        nl_SR = "nl_SR"
        nl_SX = "nl_SX"
        nmg = "nmg"
        nmg_CM = "nmg_CM"
        nn = "nn"
        nn_NO = "nn_NO"
        nus = "nus"
        nus_SD = "nus_SD"
        nyn = "nyn"
        nyn_UG = "nyn_UG"
        om = "om"
        om_ET = "om_ET"
        om_KE = "om_KE"
        or_ = "or"
        or_IN = "or_IN"
        pa = "pa"
        pa_Arab = "pa_Arab"
        pa_Arab_PK = "pa_Arab_PK"
        pa_Guru = "pa_Guru"
        pa_Guru_IN = "pa_Guru_IN"
        pl = "pl"
        pl_PL = "pl_PL"
        ps = "ps"
        ps_AF = "ps_AF"
        pt = "pt"
        pt_AO = "pt_AO"
        pt_BR = "pt_BR"
        pt_CV = "pt_CV"
        pt_GW = "pt_GW"
        pt_MO = "pt_MO"
        pt_MZ = "pt_MZ"
        pt_PT = "pt_PT"
        pt_ST = "pt_ST"
        pt_TL = "pt_TL"
        rm = "rm"
        rm_CH = "rm_CH"
        rn = "rn"
        rn_BI = "rn_BI"
        ro = "ro"
        ro_MD = "ro_MD"
        ro_RO = "ro_RO"
        rof = "rof"
        rof_TZ = "rof_TZ"
        ru = "ru"
        ru_BY = "ru_BY"
        ru_KG = "ru_KG"
        ru_KZ = "ru_KZ"
        ru_MD = "ru_MD"
        ru_RU = "ru_RU"
        ru_UA = "ru_UA"
        rw = "rw"
        rw_RW = "rw_RW"
        rwk = "rwk"
        rwk_TZ = "rwk_TZ"
        saq = "saq"
        saq_KE = "saq_KE"
        sbp = "sbp"
        sbp_TZ = "sbp_TZ"
        seh = "seh"
        seh_MZ = "seh_MZ"
        ses = "ses"
        ses_ML = "ses_ML"
        sg = "sg"
        sg_CF = "sg_CF"
        shi = "shi"
        shi_Latn = "shi_Latn"
        shi_Latn_MA = "shi_Latn_MA"
        shi_Tfng = "shi_Tfng"
        shi_Tfng_MA = "shi_Tfng_MA"
        si = "si"
        si_LK = "si_LK"
        sk = "sk"
        sk_SK = "sk_SK"
        sl = "sl"
        sl_SI = "sl_SI"
        sn = "sn"
        sn_ZW = "sn_ZW"
        so = "so"
        so_DJ = "so_DJ"
        so_ET = "so_ET"
        so_KE = "so_KE"
        so_SO = "so_SO"
        sq = "sq"
        sq_AL = "sq_AL"
        sq_MK = "sq_MK"
        sr = "sr"
        sr_Cyrl = "sr_Cyrl"
        sr_Cyrl_BA = "sr_Cyrl_BA"
        sr_Cyrl_ME = "sr_Cyrl_ME"
        sr_Cyrl_RS = "sr_Cyrl_RS"
        sr_Latn = "sr_Latn"
        sr_Latn_BA = "sr_Latn_BA"
        sr_Latn_ME = "sr_Latn_ME"
        sr_Latn_RS = "sr_Latn_RS"
        sv = "sv"
        sv_AX = "sv_AX"
        sv_FI = "sv_FI"
        sv_SE = "sv_SE"
        sw = "sw"
        sw_KE = "sw_KE"
        sw_TZ = "sw_TZ"
        sw_UG = "sw_UG"
        swc = "swc"
        swc_CD = "swc_CD"
        ta = "ta"
        ta_IN = "ta_IN"
        ta_LK = "ta_LK"
        ta_MY = "ta_MY"
        ta_SG = "ta_SG"
        te = "te"
        te_IN = "te_IN"
        teo = "teo"
        teo_KE = "teo_KE"
        teo_UG = "teo_UG"
        th = "th"
        th_TH = "th_TH"
        ti = "ti"
        ti_ER = "ti_ER"
        ti_ET = "ti_ET"
        to = "to"
        to_TO = "to_TO"
        tr = "tr"
        tr_CY = "tr_CY"
        tr_TR = "tr_TR"
        twq = "twq"
        twq_NE = "twq_NE"
        tzm = "tzm"
        tzm_Latn = "tzm_Latn"
        tzm_Latn_MA = "tzm_Latn_MA"
        uk = "uk"
        uk_UA = "uk_UA"
        ur = "ur"
        ur_IN = "ur_IN"
        ur_PK = "ur_PK"
        uz = "uz"
        uz_Arab = "uz_Arab"
        uz_Arab_AF = "uz_Arab_AF"
        uz_Cyrl = "uz_Cyrl"
        uz_Cyrl_UZ = "uz_Cyrl_UZ"
        uz_Latn = "uz_Latn"
        uz_Latn_UZ = "uz_Latn_UZ"
        vai = "vai"
        vai_Latn = "vai_Latn"
        vai_Latn_LR = "vai_Latn_LR"
        vai_Vaii = "vai_Vaii"
        vai_Vaii_LR = "vai_Vaii_LR"
        vi = "vi"
        vi_VN = "vi_VN"
        vun = "vun"
        vun_TZ = "vun_TZ"
        xog = "xog"
        xog_UG = "xog_UG"
        yav = "yav"
        yav_CM = "yav_CM"
        yo = "yo"
        yo_NG = "yo_NG"
        zh = "zh"
        zh_Hans = "zh_Hans"
        zh_Hans_CN = "zh_Hans_CN"
        zh_Hans_HK = "zh_Hans_HK"
        zh_Hans_MO = "zh_Hans_MO"
        zh_Hans_SG = "zh_Hans_SG"
        zh_Hant = "zh_Hant"
        zh_Hant_HK = "zh_Hant_HK"
        zh_Hant_MO = "zh_Hant_MO"
        zh_Hant_TW = "zh_Hant_TW"
        zu = "zu"
        zu_ZA = "zu_ZA"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class FILESET:
    """Enums for properties in the FILESET stage."""

    class CreateReplaceDiscardRecordsDiscardSchemaAndRecords(Enum):
        """Enum for the CreateReplaceDiscardRecordsDiscardSchemaAndRecords property."""

        discard_records = "discard_records"
        replace = "replace"
        discard_schema_and_records = "discard_schema_and_records"
        create = "create"

    class OmitSchemaWriteSchema(Enum):
        """Enum for the OmitSchemaWriteSchema property."""

        writeSchema = "writeSchema"
        omitSchema = "omitSchema"

    class RejectMode(Enum):
        """Enum for the RejectMode property."""

        save = "save"
        cont = "continue"
        fail = "fail"

    class CleanupOnFailure(Enum):
        """Enum for the CleanupOnFailure property."""

        false = " "
        true = "nocleanup"

    class SingleFilePerPartition(Enum):
        """Enum for the SingleFilePerPartition property."""

        true = "singleFilePerPartition"
        false = " "

    class UseSchemaDefinedInFileSet(Enum):
        """Enum for the UseSchemaDefinedInFileSet property."""

        true = "schemafileset"
        false = " "

    class StripBom(Enum):
        """Enum for the StripBom property."""

        true = "stripbom"
        false = " "

    class KeepPartitions(Enum):
        """Enum for the KeepPartitions property."""

        true = "keepPartitions"
        false = " "

    class ReportProgress(Enum):
        """Enum for the ReportProgress property."""

        no = "no"
        yes = "yes"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_set = -2
        default_clear = -1
        clear = 0
        set = 1

    class MapName(Enum):
        """Enum for the MapName property."""

        Adobe_Standard_Encoding = "Adobe-Standard-Encoding"
        ANSI_X3_4_1968 = "ANSI_X3.4-1968"
        ASCL_ASCII = "ASCL_ASCII"
        ASCL_ASCII_PC1 = "ASCL_ASCII-PC1"
        ASCL_BIG5 = "ASCL_BIG5"
        ASCL_C0_CONTROLS = "ASCL_C0-CONTROLS"
        ASCL_C1_CONTROLS = "ASCL_C1-CONTROLS"
        ASCL_EBCDIC = "ASCL_EBCDIC"
        ASCL_EBCDIC_037 = "ASCL_EBCDIC-037"
        ASCL_EBCDIC_1026 = "ASCL_EBCDIC-1026"
        ASCL_EBCDIC_500V1 = "ASCL_EBCDIC-500V1"
        ASCL_EBCDIC_875 = "ASCL_EBCDIC-875"
        ASCL_EBCDIC_CTRLS = "ASCL_EBCDIC-CTRLS"
        ASCL_EBCDIC_IBM1364 = "ASCL_EBCDIC-IBM1364"
        ASCL_EBCDIC_IBM1371 = "ASCL_EBCDIC-IBM1371"
        ASCL_EBCDIC_IBM933 = "ASCL_EBCDIC-IBM933"
        ASCL_EBCDIC_IBM937 = "ASCL_EBCDIC-IBM937"
        ASCL_EBCDIC_JP_CTRLS = "ASCL_EBCDIC-JP-CTRLS"
        ASCL_EBCDIC_JP_KANA = "ASCL_EBCDIC-JP-KANA"
        ASCL_EBCDIC_JP_KANA_E = "ASCL_EBCDIC-JP-KANA-E"
        ASCL_EBCDIC_JP_KANA_HW = "ASCL_EBCDIC-JP-KANA-HW"
        ASCL_GB2312 = "ASCL_GB2312"
        ASCL_ISO8859_1 = "ASCL_ISO8859-1"
        ASCL_ISO8859_10 = "ASCL_ISO8859-10"
        ASCL_ISO8859_15 = "ASCL_ISO8859-15"
        ASCL_ISO8859_2 = "ASCL_ISO8859-2"
        ASCL_ISO8859_3 = "ASCL_ISO8859-3"
        ASCL_ISO8859_4 = "ASCL_ISO8859-4"
        ASCL_ISO8859_5 = "ASCL_ISO8859-5"
        ASCL_ISO8859_6 = "ASCL_ISO8859-6"
        ASCL_ISO8859_7 = "ASCL_ISO8859-7"
        ASCL_ISO8859_8 = "ASCL_ISO8859-8"
        ASCL_ISO8859_9 = "ASCL_ISO8859-9"
        ASCL_JIS_EUC = "ASCL_JIS-EUC"
        ASCL_JIS_EUC_HWK = "ASCL_JIS-EUC-HWK"
        ASCL_JIS_EUC_P = "ASCL_JIS-EUC-P"
        ASCL_JIS_ROMAN = "ASCL_JIS-ROMAN"
        ASCL_JISX0201 = "ASCL_JISX0201"
        ASCL_JPN_EBCDIC = "ASCL_JPN-EBCDIC"
        ASCL_JPN_EBCDIK = "ASCL_JPN-EBCDIK"
        ASCL_JPN_EBCDIKC_CTRL = "ASCL_JPN-EBCDIKC-CTRL"
        ASCL_JPN_EUC = "ASCL_JPN-EUC"
        ASCL_JPN_EUC_KAT = "ASCL_JPN-EUC-KAT"
        ASCL_JPN_EUC_ONE = "ASCL_JPN-EUC-ONE"
        ASCL_JPN_EUC_RTE = "ASCL_JPN-EUC-RTE"
        ASCL_JPN_EUC_TWO = "ASCL_JPN-EUC-TWO"
        ASCL_JPN_IBM78 = "ASCL_JPN-IBM78"
        ASCL_JPN_IBM83 = "ASCL_JPN-IBM83"
        ASCL_JPN_JEF78 = "ASCL_JPN-JEF78"
        ASCL_JPN_JEF83 = "ASCL_JPN-JEF83"
        ASCL_JPN_JIPSE = "ASCL_JPN-JIPSE"
        ASCL_JPN_JIPSJ = "ASCL_JPN-JIPSJ"
        ASCL_JPN_JIS_RTE = "ASCL_JPN-JIS-RTE"
        ASCL_JPN_JIS8 = "ASCL_JPN-JIS8"
        ASCL_JPN_JIS8EUC_CTRL = "ASCL_JPN-JIS8EUC-CTRL"
        ASCL_JPN_KEIS_RTE = "ASCL_JPN-KEIS-RTE"
        ASCL_JPN_KEIS78 = "ASCL_JPN-KEIS78"
        ASCL_JPN_KEIS83 = "ASCL_JPN-KEIS83"
        ASCL_JPN_NEBCDIK = "ASCL_JPN-NEBCDIK"
        ASCL_JPN_SJIS = "ASCL_JPN-SJIS"
        ASCL_KOI8_R = "ASCL_KOI8-R"
        ASCL_KSC5601 = "ASCL_KSC5601"
        ASCL_KSC5601_1992 = "ASCL_KSC5601-1992"
        ASCL_MAC_GREEK = "ASCL_MAC-GREEK"
        ASCL_MAC_GREEK2 = "ASCL_MAC-GREEK2"
        ASCL_MAC_ROMAN = "ASCL_MAC-ROMAN"
        ASCL_MNEMONICS = "ASCL_MNEMONICS"
        ASCL_MS1250 = "ASCL_MS1250"
        ASCL_MS1251 = "ASCL_MS1251"
        ASCL_MS1252 = "ASCL_MS1252"
        ASCL_MS1253 = "ASCL_MS1253"
        ASCL_MS1254 = "ASCL_MS1254"
        ASCL_MS1255 = "ASCL_MS1255"
        ASCL_MS1256 = "ASCL_MS1256"
        ASCL_MS932 = "ASCL_MS932"
        ASCL_MS932_BASE = "ASCL_MS932-BASE"
        ASCL_MS932_EXTRA = "ASCL_MS932-EXTRA"
        ASCL_MS936 = "ASCL_MS936"
        ASCL_MS936_BASE = "ASCL_MS936-BASE"
        ASCL_MS949 = "ASCL_MS949"
        ASCL_MS950 = "ASCL_MS950"
        ASCL_MS950_BASE = "ASCL_MS950-BASE"
        ASCL_PC1040 = "ASCL_PC1040"
        ASCL_PC1041 = "ASCL_PC1041"
        ASCL_PC437 = "ASCL_PC437"
        ASCL_PC850 = "ASCL_PC850"
        ASCL_PC852 = "ASCL_PC852"
        ASCL_PC855 = "ASCL_PC855"
        ASCL_PC857 = "ASCL_PC857"
        ASCL_PC860 = "ASCL_PC860"
        ASCL_PC861 = "ASCL_PC861"
        ASCL_PC862 = "ASCL_PC862"
        ASCL_PC863 = "ASCL_PC863"
        ASCL_PC864 = "ASCL_PC864"
        ASCL_PC865 = "ASCL_PC865"
        ASCL_PC866 = "ASCL_PC866"
        ASCL_PC869 = "ASCL_PC869"
        ASCL_PC874 = "ASCL_PC874"
        ASCL_PRIME_SHIFT_JIS = "ASCL_PRIME-SHIFT-JIS"
        ASCL_SHIFT_JIS = "ASCL_SHIFT-JIS"
        ASCL_TAU_SHIFT_JIS = "ASCL_TAU-SHIFT-JIS"
        ASCL_TIS620 = "ASCL_TIS620"
        ASCL_TIS620_B = "ASCL_TIS620-B"
        Big5 = "Big5"
        Big5_HKSCS = "Big5-HKSCS"
        BOCU_1 = "BOCU-1"
        CESU_8 = "CESU-8"
        ebcdic_xml_us = "ebcdic-xml-us"
        EUC_KR = "EUC-KR"
        GB_2312_80 = "GB_2312-80"
        gb18030_gb18030 = "gb18030 gb18030"
        GB2312 = "GB2312"
        GBK = "GBK"
        hp_roman8 = "hp-roman8"
        HZ_HZ_GB_2312 = "HZ HZ-GB-2312"
        ibm_1006_P100_1995 = "ibm-1006_P100-1995"
        ibm_1025_P100_1995 = "ibm-1025_P100-1995"
        ibm_1026_P100_1995 = "ibm-1026_P100-1995"
        ibm_1047_P100_1995 = "ibm-1047_P100-1995"
        ibm_1047_P100_1995_swaplfnl = "ibm-1047_P100-1995,swaplfnl"
        ibm_1051_P100_1995 = "ibm-1051_P100-1995"
        ibm_1089_P100_1995 = "ibm-1089_P100-1995"
        ibm_1097_P100_1995 = "ibm-1097_P100-1995"
        ibm_1098_P100_1995 = "ibm-1098_P100-1995"
        ibm_1112_P100_1995 = "ibm-1112_P100-1995"
        ibm_1122_P100_1999 = "ibm-1122_P100-1999"
        ibm_1123_P100_1995 = "ibm-1123_P100-1995"
        ibm_1124_P100_1996 = "ibm-1124_P100-1996"
        ibm_1125_P100_1997 = "ibm-1125_P100-1997"
        ibm_1129_P100_1997 = "ibm-1129_P100-1997"
        ibm_1130_P100_1997 = "ibm-1130_P100-1997"
        ibm_1131_P100_1997 = "ibm-1131_P100-1997"
        ibm_1132_P100_1998 = "ibm-1132_P100-1998"
        ibm_1133_P100_1997 = "ibm-1133_P100-1997"
        ibm_1137_P100_1999 = "ibm-1137_P100-1999"
        ibm_1140_P100_1997 = "ibm-1140_P100-1997"
        ibm_1140_P100_1997_swaplfnl = "ibm-1140_P100-1997,swaplfnl"
        ibm_1141_P100_1997 = "ibm-1141_P100-1997"
        ibm_1141_P100_1997_swaplfnl = "ibm-1141_P100-1997,swaplfnl"
        ibm_1142_P100_1997 = "ibm-1142_P100-1997"
        ibm_1142_P100_1997_swaplfnl = "ibm-1142_P100-1997,swaplfnl"
        ibm_1143_P100_1997 = "ibm-1143_P100-1997"
        ibm_1143_P100_1997_swaplfnl = "ibm-1143_P100-1997,swaplfnl"
        ibm_1144_P100_1997 = "ibm-1144_P100-1997"
        ibm_1144_P100_1997_swaplfnl = "ibm-1144_P100-1997,swaplfnl"
        ibm_1145_P100_1997 = "ibm-1145_P100-1997"
        ibm_1145_P100_1997_swaplfnl = "ibm-1145_P100-1997,swaplfnl"
        ibm_1146_P100_1997 = "ibm-1146_P100-1997"
        ibm_1146_P100_1997_swaplfnl = "ibm-1146_P100-1997,swaplfnl"
        ibm_1147_P100_1997 = "ibm-1147_P100-1997"
        ibm_1147_P100_1997_swaplfnl = "ibm-1147_P100-1997,swaplfnl"
        ibm_1148_P100_1997 = "ibm-1148_P100-1997"
        ibm_1148_P100_1997_swaplfnl = "ibm-1148_P100-1997,swaplfnl"
        ibm_1149_P100_1997 = "ibm-1149_P100-1997"
        ibm_1149_P100_1997_swaplfnl = "ibm-1149_P100-1997,swaplfnl"
        ibm_1153_P100_1999 = "ibm-1153_P100-1999"
        ibm_1153_P100_1999_swaplfnl = "ibm-1153_P100-1999,swaplfnl"
        ibm_1154_P100_1999 = "ibm-1154_P100-1999"
        ibm_1155_P100_1999 = "ibm-1155_P100-1999"
        ibm_1156_P100_1999 = "ibm-1156_P100-1999"
        ibm_1157_P100_1999 = "ibm-1157_P100-1999"
        ibm_1158_P100_1999 = "ibm-1158_P100-1999"
        ibm_1160_P100_1999 = "ibm-1160_P100-1999"
        ibm_1162_P100_1999 = "ibm-1162_P100-1999"
        ibm_1164_P100_1999 = "ibm-1164_P100-1999"
        ibm_1168_P100_2002 = "ibm-1168_P100-2002"
        ibm_1250_P100_1995 = "ibm-1250_P100-1995"
        ibm_1251_P100_1995 = "ibm-1251_P100-1995"
        ibm_1252_P100_2000 = "ibm-1252_P100-2000"
        ibm_1253_P100_1995 = "ibm-1253_P100-1995"
        ibm_1254_P100_1995 = "ibm-1254_P100-1995"
        ibm_1255_P100_1995 = "ibm-1255_P100-1995"
        ibm_1256_P110_1997 = "ibm-1256_P110-1997"
        ibm_1257_P100_1995 = "ibm-1257_P100-1995"
        ibm_1258_P100_1997 = "ibm-1258_P100-1997"
        ibm_12712_P100_1998 = "ibm-12712_P100-1998"
        ibm_12712_P100_1998_swaplfnl = "ibm-12712_P100-1998,swaplfnl"
        ibm_1276_P100_1995 = "ibm-1276_P100-1995"
        ibm_1277_P100_1995 = "ibm-1277_P100-1995"
        ibm_1363_P110_1997 = "ibm-1363_P110-1997"
        ibm_1363_P11B_1998 = "ibm-1363_P11B-1998"
        ibm_1364_P110_1997 = "ibm-1364_P110-1997"
        ibm_1364_P110_2007 = "ibm-1364_P110-2007"
        ibm_1371_P100_1999 = "ibm-1371_P100-1999"
        ibm_1373_P100_2002 = "ibm-1373_P100-2002"
        ibm_1375_P100_2003 = "ibm-1375_P100-2003"
        ibm_1375_P100_2007 = "ibm-1375_P100-2007"
        ibm_1381_P110_1999 = "ibm-1381_P110-1999"
        ibm_1383_P110_1999 = "ibm-1383_P110-1999"
        ibm_1386_P100_2001 = "ibm-1386_P100-2001"
        ibm_1386_P100_2002 = "ibm-1386_P100-2002"
        ibm_1388_P103_2001 = "ibm-1388_P103-2001"
        ibm_1390_P110_2003 = "ibm-1390_P110-2003"
        ibm_1399_P110_2003 = "ibm-1399_P110-2003"
        ibm_16684_P110_2003 = "ibm-16684_P110-2003"
        ibm_16804_X110_1999 = "ibm-16804_X110-1999"
        ibm_16804_X110_1999_swaplfnl = "ibm-16804_X110-1999,swaplfnl"
        ibm_273_P100_1995 = "ibm-273_P100-1995"
        ibm_277_P100_1995 = "ibm-277_P100-1995"
        ibm_278_P100_1995 = "ibm-278_P100-1995"
        ibm_280_P100_1995 = "ibm-280_P100-1995"
        ibm_284_P100_1995 = "ibm-284_P100-1995"
        ibm_285_P100_1995 = "ibm-285_P100-1995"
        ibm_290_P100_1995 = "ibm-290_P100-1995"
        ibm_297_P100_1995 = "ibm-297_P100-1995"
        ibm_33722_P120_1999 = "ibm-33722_P120-1999"
        ibm_33722_P12A_P12A_2009_U2_Extended_UNIX_Code_Packed_Format_for_Japanese = (
            "ibm-33722_P12A_P12A-2009_U2 Extended_UNIX_Code_Packed_Format_for_Japanese"
        )
        ibm_33722_P12A_1999 = "ibm-33722_P12A-1999"
        ibm_367_P100_1995 = "ibm-367_P100-1995"
        ibm_37_P100_1995 = "ibm-37_P100-1995"
        ibm_37_P100_1995_swaplfnl = "ibm-37_P100-1995,swaplfnl"
        ibm_420_X120_1999 = "ibm-420_X120-1999"
        ibm_424_P100_1995 = "ibm-424_P100-1995"
        ibm_437_P100_1995 = "ibm-437_P100-1995"
        ibm_4517_P100_2005 = "ibm-4517_P100-2005"
        ibm_4899_P100_1998 = "ibm-4899_P100-1998"
        ibm_4909_P100_1999 = "ibm-4909_P100-1999"
        ibm_4971_P100_1999 = "ibm-4971_P100-1999"
        ibm_500_P100_1995 = "ibm-500_P100-1995"
        ibm_5012_P100_1999 = "ibm-5012_P100-1999"
        ibm_5123_P100_1999 = "ibm-5123_P100-1999"
        ibm_5346_P100_1998 = "ibm-5346_P100-1998"
        ibm_5347_P100_1998 = "ibm-5347_P100-1998"
        ibm_5348_P100_1997 = "ibm-5348_P100-1997"
        ibm_5349_P100_1998 = "ibm-5349_P100-1998"
        ibm_5350_P100_1998 = "ibm-5350_P100-1998"
        ibm_5351_P100_1998 = "ibm-5351_P100-1998"
        ibm_5352_P100_1998 = "ibm-5352_P100-1998"
        ibm_5353_P100_1998 = "ibm-5353_P100-1998"
        ibm_5354_P100_1998 = "ibm-5354_P100-1998"
        ibm_5471_P100_2006 = "ibm-5471_P100-2006"
        ibm_5478_P100_1995 = "ibm-5478_P100-1995"
        ibm_720_P100_1997 = "ibm-720_P100-1997"
        ibm_737_P100_1997 = "ibm-737_P100-1997"
        ibm_775_P100_1996 = "ibm-775_P100-1996"
        ibm_803_P100_1999 = "ibm-803_P100-1999"
        ibm_813_P100_1995 = "ibm-813_P100-1995"
        ibm_838_P100_1995 = "ibm-838_P100-1995"
        ibm_8482_P100_1999 = "ibm-8482_P100-1999"
        ibm_850_P100_1995 = "ibm-850_P100-1995"
        ibm_851_P100_1995 = "ibm-851_P100-1995"
        ibm_852_P100_1995 = "ibm-852_P100-1995"
        ibm_855_P100_1995 = "ibm-855_P100-1995"
        ibm_856_P100_1995 = "ibm-856_P100-1995"
        ibm_857_P100_1995 = "ibm-857_P100-1995"
        ibm_858_P100_1997 = "ibm-858_P100-1997"
        ibm_860_P100_1995 = "ibm-860_P100-1995"
        ibm_861_P100_1995 = "ibm-861_P100-1995"
        ibm_862_P100_1995 = "ibm-862_P100-1995"
        ibm_863_P100_1995 = "ibm-863_P100-1995"
        ibm_864_X110_1999 = "ibm-864_X110-1999"
        ibm_865_P100_1995 = "ibm-865_P100-1995"
        ibm_866_P100_1995 = "ibm-866_P100-1995"
        ibm_867_P100_1998 = "ibm-867_P100-1998"
        ibm_868_P100_1995 = "ibm-868_P100-1995"
        ibm_869_P100_1995 = "ibm-869_P100-1995"
        ibm_870_P100_1995 = "ibm-870_P100-1995"
        ibm_871_P100_1995 = "ibm-871_P100-1995"
        ibm_874_P100_1995 = "ibm-874_P100-1995"
        ibm_875_P100_1995 = "ibm-875_P100-1995"
        ibm_878_P100_1996 = "ibm-878_P100-1996"
        ibm_897_P100_1995 = "ibm-897_P100-1995"
        ibm_9005_X110_2007 = "ibm-9005_X110-2007"
        ibm_901_P100_1999 = "ibm-901_P100-1999"
        ibm_902_P100_1999 = "ibm-902_P100-1999"
        ibm_9067_X100_2005 = "ibm-9067_X100-2005"
        ibm_912_P100_1995 = "ibm-912_P100-1995"
        ibm_913_P100_2000 = "ibm-913_P100-2000"
        ibm_914_P100_1995 = "ibm-914_P100-1995"
        ibm_915_P100_1995 = "ibm-915_P100-1995"
        ibm_916_P100_1995 = "ibm-916_P100-1995"
        ibm_918_P100_1995 = "ibm-918_P100-1995"
        ibm_920_P100_1995 = "ibm-920_P100-1995"
        ibm_921_P100_1995 = "ibm-921_P100-1995"
        ibm_922_P100_1999 = "ibm-922_P100-1999"
        ibm_923_P100_1998 = "ibm-923_P100-1998"
        ibm_930_P120_1999 = "ibm-930_P120-1999"
        ibm_933_P110_1995 = "ibm-933_P110-1995"
        ibm_935_P110_1999 = "ibm-935_P110-1999"
        ibm_937_P110_1999 = "ibm-937_P110-1999"
        ibm_939_P120_1999 = "ibm-939_P120-1999"
        ibm_942_P12A_1999 = "ibm-942_P12A-1999"
        ibm_943_P130_1999 = "ibm-943_P130-1999"
        ibm_943_P15A_2003 = "ibm-943_P15A-2003"
        ibm_9447_P100_2002 = "ibm-9447_P100-2002"
        ibm_9448_X100_2005 = "ibm-9448_X100-2005"
        ibm_9449_P100_2002 = "ibm-9449_P100-2002"
        ibm_949_P110_1999 = "ibm-949_P110-1999"
        ibm_949_P11A_1999 = "ibm-949_P11A-1999"
        ibm_950_P110_1999 = "ibm-950_P110-1999"
        ibm_954_P101_2000 = "ibm-954_P101-2000"
        ibm_954_P101_2007 = "ibm-954_P101-2007"
        ibm_964_P110_1999 = "ibm-964_P110-1999"
        ibm_970_P110_P110_2006_U2 = "ibm-970_P110_P110-2006_U2"
        ibm_970_P110_1995 = "ibm-970_P110-1995"
        ibm_971_P100_1995 = "ibm-971_P100-1995"
        IBM_Thai = "IBM-Thai"
        IBM00858 = "IBM00858"
        IBM01140 = "IBM01140"
        IBM01141 = "IBM01141"
        IBM01142 = "IBM01142"
        IBM01143 = "IBM01143"
        IBM01144 = "IBM01144"
        IBM01145 = "IBM01145"
        IBM01146 = "IBM01146"
        IBM01147 = "IBM01147"
        IBM01148 = "IBM01148"
        IBM01149 = "IBM01149"
        IBM037 = "IBM037"
        IBM1026 = "IBM1026"
        IBM1047 = "IBM1047"
        IBM273 = "IBM273"
        IBM277 = "IBM277"
        IBM278 = "IBM278"
        IBM280 = "IBM280"
        IBM284 = "IBM284"
        IBM285 = "IBM285"
        IBM290 = "IBM290"
        IBM297 = "IBM297"
        IBM420 = "IBM420"
        IBM424 = "IBM424"
        IBM437 = "IBM437"
        IBM500 = "IBM500"
        IBM775 = "IBM775"
        IBM850 = "IBM850"
        IBM851 = "IBM851"
        IBM852 = "IBM852"
        IBM855 = "IBM855"
        IBM857 = "IBM857"
        IBM860 = "IBM860"
        IBM861 = "IBM861"
        IBM862 = "IBM862"
        IBM863 = "IBM863"
        IBM864 = "IBM864"
        IBM865 = "IBM865"
        IBM866 = "IBM866"
        IBM868 = "IBM868"
        IBM869 = "IBM869"
        IBM870 = "IBM870"
        IBM871 = "IBM871"
        IBM918 = "IBM918"
        IMAP_mailbox_name = "IMAP-mailbox-name"
        ISCII_version_0 = "ISCII,version=0"
        ISCII_version_1 = "ISCII,version=1"
        ISCII_version_2 = "ISCII,version=2"
        ISCII_version_3 = "ISCII,version=3"
        ISCII_version_4 = "ISCII,version=4"
        ISCII_version_5 = "ISCII,version=5"
        ISCII_version_6 = "ISCII,version=6"
        ISCII_version_7 = "ISCII,version=7"
        ISCII_version_8 = "ISCII,version=8"
        ISO_2022_locale_ja_version_0 = "ISO_2022,locale=ja,version=0"
        ISO_2022_locale_ja_version_1 = "ISO_2022,locale=ja,version=1"
        ISO_2022_locale_ja_version_2 = "ISO_2022,locale=ja,version=2"
        ISO_2022_locale_ja_version_3 = "ISO_2022,locale=ja,version=3"
        ISO_2022_locale_ja_version_4 = "ISO_2022,locale=ja,version=4"
        ISO_2022_locale_ko_version_0 = "ISO_2022,locale=ko,version=0"
        ISO_2022_locale_ko_version_1 = "ISO_2022,locale=ko,version=1"
        ISO_2022_locale_zh_version_0 = "ISO_2022,locale=zh,version=0"
        ISO_2022_locale_zh_version_1 = "ISO_2022,locale=zh,version=1"
        ISO_2022_locale_zh_version_2 = "ISO_2022,locale=zh,version=2"
        ISO_8859_1_1987 = "ISO_8859-1:1987"
        ISO_8859_2_1987 = "ISO_8859-2:1987"
        ISO_8859_3_1988 = "ISO_8859-3:1988"
        ISO_8859_4_1988 = "ISO_8859-4:1988"
        ISO_8859_5_1988 = "ISO_8859-5:1988"
        ISO_8859_6_1987 = "ISO_8859-6:1987"
        ISO_8859_7_1987 = "ISO_8859-7:1987"
        ISO_8859_8_1988 = "ISO_8859-8:1988"
        ISO_8859_9_1989 = "ISO_8859-9:1989"
        ISO_2022_CN = "ISO-2022-CN"
        ISO_2022_CN_EXT = "ISO-2022-CN-EXT"
        ISO_2022_JP = "ISO-2022-JP"
        ISO_2022_JP_2 = "ISO-2022-JP-2"
        ISO_2022_KR = "ISO-2022-KR"
        iso_8859_10_1998 = "iso-8859_10-1998"
        iso_8859_11_2001 = "iso-8859_11-2001"
        iso_8859_14_1998 = "iso-8859_14-1998"
        ISO_8859_1 = "ISO-8859-1"
        ISO_8859_10 = "ISO-8859-10"
        ISO_8859_13 = "ISO-8859-13"
        ISO_8859_14 = "ISO-8859-14"
        ISO_8859_15 = "ISO-8859-15"
        JIS_Encoding = "JIS_Encoding"
        KOI8_R = "KOI8-R"
        KOI8_U = "KOI8-U"
        KS_C_5601_1987 = "KS_C_5601-1987"
        LMBCS_1 = "LMBCS-1"
        macintosh = "macintosh"
        macos_0_2_10_2 = "macos-0_2-10.2"
        macos_2566_10_2 = "macos-2566-10.2"
        macos_29_10_2 = "macos-29-10.2"
        macos_35_10_2 = "macos-35-10.2"
        macos_6_2_10_4 = "macos-6_2-10.4"
        macos_6_10_2 = "macos-6-10.2"
        macos_7_3_10_2 = "macos-7_3-10.2"
        SCSU = "SCSU"
        Shift_JIS = "Shift_JIS"
        TIS_620 = "TIS-620"
        US_ASCII = "US-ASCII"
        UTF_16 = "UTF-16"
        UTF_16_version_1 = "UTF-16,version=1"
        UTF_16_version_2 = "UTF-16,version=2"
        UTF_16BE = "UTF-16BE"
        UTF_16BE_version_1 = "UTF-16BE,version=1"
        UTF_16LE = "UTF-16LE"
        UTF_16LE_version_1 = "UTF-16LE,version=1"
        UTF_32 = "UTF-32"
        UTF_32BE = "UTF-32BE"
        UTF_32LE = "UTF-32LE"
        UTF_7 = "UTF-7"
        UTF_8 = "UTF-8"
        UTF16_OppositeEndian = "UTF16_OppositeEndian"
        UTF16_PlatformEndian = "UTF16_PlatformEndian"
        UTF32_OppositeEndian = "UTF32_OppositeEndian"
        UTF32_PlatformEndian = "UTF32_PlatformEndian"
        windows_1250 = "windows-1250"
        windows_1251 = "windows-1251"
        windows_1252 = "windows-1252"
        windows_1253 = "windows-1253"
        windows_1254 = "windows-1254"
        windows_1255 = "windows-1255"
        windows_1256 = "windows-1256"
        windows_1256_2000 = "windows-1256-2000"
        windows_1257 = "windows-1257"
        windows_1258 = "windows-1258"
        windows_874_2000 = "windows-874-2000"
        windows_936_2000 = "windows-936-2000"
        windows_949_2000 = "windows-949-2000"
        windows_950_2000 = "windows-950-2000"
        x11_compound_text = "x11-compound-text"

    class AllowPerColumnMapping(Enum):
        """Enum for the AllowPerColumnMapping property."""

        false = "False"
        true = "True"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class FinalDelimiter(Enum):
        """Enum for the FinalDelimiter property."""

        custom = " "
        ws = "ws"
        end = "end"
        none = "none"
        null = "null"
        comma = "','"
        tab = "'\t'"

    class FillChar(Enum):
        """Enum for the FillChar property."""

        custom_fill_char = -1
        null = 0

    class CheckIntact(Enum):
        """Enum for the CheckIntact property."""

        check_intact = "check_intact"

    class RecordDelimiter(Enum):
        """Enum for the RecordDelimiter property."""

        custom = " "
        newline = "'\n'"
        null = "null"

    class RecordPrefix(Enum):
        """Enum for the RecordPrefix property."""

        one = 1
        two = 2
        four = 4

    class RecordLength(Enum):
        """Enum for the RecordLength property."""

        custom = " "
        fixed = "fixed"

    class RecordType(Enum):
        """Enum for the RecordType property."""

        type_implicit = "{type=implicit}"
        type_varying = "{type=varying}"
        type_varying_format_V = "{type=varying, format=V}"
        type_varying_format_VB = "{type=varying, format=VB}"
        type_varying_format_VBS = "{type=varying, format=VBS}"
        type_varying_format_VR = "{type=varying, format=VR}"
        type_varying_format_VS = "{type=varying, format=VS}"

    class Delimiter(Enum):
        """Enum for the Delimiter property."""

        custom = " "
        ws = "ws"
        end = "end"
        none = "none"
        null = "null"
        comma = "','"
        tab = "'\t'"

    class Quote(Enum):
        """Enum for the Quote property."""

        custom = " "
        single = "single"
        double = "double"
        none = "none"

    class NullFieldValueSeparator(Enum):
        """Enum for the NullFieldValueSeparator property."""

        space = " "
        comma = "','"

    class PrintField(Enum):
        """Enum for the PrintField property."""

        print_field = "print_field"

    class VectorPrefix(Enum):
        """Enum for the VectorPrefix property."""

        one = 1
        two = 2
        four = 4

    class PrefixBytes(Enum):
        """Enum for the PrefixBytes property."""

        one = 1
        two = 2
        four = 4

    class ByteOrder(Enum):
        """Enum for the ByteOrder property."""

        little_endian = "little_endian"
        big_endian = "big_endian"
        native_endian = "native_endian"

    class CharacterSet(Enum):
        """Enum for the CharacterSet property."""

        ebcdic = "ebcdic"
        ascii = "ascii"

    class DataFormat(Enum):
        """Enum for the DataFormat property."""

        binary = "binary"
        text = "text"

    class PadChar(Enum):
        """Enum for the PadChar property."""

        custom = " "
        false_ = "' '"
        null = "null"

    class ExportEbcdicAsAscii(Enum):
        """Enum for the ExportEbcdicAsAscii property."""

        export_ebcdic_as_ascii = "export_ebcdic_as_ascii"

    class ImportAsciiAsEbcdic(Enum):
        """Enum for the ImportAsciiAsEbcdic property."""

        import_ascii_as_ebcdic = "import_ascii_as_ebcdic"

    class AllowAllZeros(Enum):
        """Enum for the AllowAllZeros property."""

        nofix_zero = "nofix_zero"
        fix_zero = "fix_zero"

    class DecimalSeparator(Enum):
        """Enum for the DecimalSeparator property."""

        custom = " "
        comma = "','"
        period = "'.'"

    class DecimalPacked(Enum):
        """Enum for the DecimalPacked property."""

        packed = "packed"
        separate = "separate"
        zoned = "zoned"
        overpunch = "overpunch"

    class DecimalPackedCheck(Enum):
        """Enum for the DecimalPackedCheck property."""

        check = "check"
        nocheck = "nocheck"

    class DecimalPackedSigned(Enum):
        """Enum for the DecimalPackedSigned property."""

        signed = "signed"
        unsigned = "unsigned"

    class AllowSignedImport(Enum):
        """Enum for the AllowSignedImport property."""

        allow_signed_import = "allow_signed_import"

    class DecimalPackedSignPosition(Enum):
        """Enum for the DecimalPackedSignPosition property."""

        trailing = "trailing"
        leading = "leading"

    class Rounding(Enum):
        """Enum for the Rounding property."""

        ceil = "ceil"
        floor = "floor"
        round_inf = "round_inf"
        trunc_zero = "trunc_zero"

    class IsJulian(Enum):
        """Enum for the IsJulian property."""

        julian = "julian"

    class IsMidnightSeconds(Enum):
        """Enum for the IsMidnightSeconds property."""

        midnight_seconds = "midnight_seconds"

    class RecLevelOption(Enum):
        """Enum for the RecLevelOption property."""

        final_delimiter = "final_delimiter"
        fill = "fill"
        final_delim_string = "final_delim_string"
        intact = "intact"
        record_delimiter = "record_delimiter"
        record_delim_string = "record_delim_string"
        record_length = "record_length"
        record_prefix = "record_prefix"
        record_format = "record_format"

    class FieldOption(Enum):
        """Enum for the FieldOption property."""

        delimiter = "delimiter"
        quote = "quote"
        actual_length = "actual_length"
        delim_string = "delim_string"
        null_length = "null_length"
        null_field = "null_field"
        prefix_bytes = "prefix_bytes"
        print_field = "print_field"
        vector_prefix = "vector_prefix"

    class GeneralOption(Enum):
        """Enum for the GeneralOption property."""

        byte_order = "byte_order"
        charset = "charset"
        data_format = "data_format"
        max_width = "max_width"
        field_width = "field_width"
        padchar = "padchar"

    class StringOption(Enum):
        """Enum for the StringOption property."""

        export_ebcdic_as_ascii = "export_ebcdic_as_ascii"
        import_ascii_as_ebcdic = "import_ascii_as_ebcdic"

    class DecimalOption(Enum):
        """Enum for the DecimalOption property."""

        allow_all_zeros = "allow_all_zeros"
        decimal_separator = "decimal_separator"
        decimal_packed = "decimal_packed"
        precision = "precision"
        round = "round"
        scale = "scale"

    class NumericOption(Enum):
        """Enum for the NumericOption property."""

        c_format = "c_format"
        in_format = "in_format"
        out_format = "out_format"

    class DateOption(Enum):
        """Enum for the DateOption property."""

        none = "none"
        days_since = "days_since"
        date_format = "date_format"
        is_julian = "is_julian"

    class TimeOption(Enum):
        """Enum for the TimeOption property."""

        none = "none"
        time_format = "time_format"
        is_midnight_seconds = "is_midnight_seconds"

    class TimestampOption(Enum):
        """Enum for the TimestampOption property."""

        none = "none"
        timestamp_format = "timestamp_format"


class SURROGATE_KEY_GENERATOR:
    """Enums for properties in the SURROGATE_KEY_GENERATOR stage."""

    class Viewonly(Enum):
        """Enum for the Viewonly property."""

        no = " "
        yes = "admin viewonly"

    class Admin(Enum):
        """Enum for the Admin property."""

        delete = "delete"
        create = "create"

    class UpdateAction(Enum):
        """Enum for the UpdateAction property."""

        admin_create = "admin create"
        admin_update = "admin update"

    class Keysourcetype(Enum):
        """Enum for the Keysourcetype property."""

        file = "file"
        dbsequence = "dbsequence"

    class AsSequencer(Enum):
        """Enum for the AsSequencer property."""

        false = " "
        true = "asSequencer"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class Dbtype(Enum):
        """Enum for the Dbtype property."""

        db2 = "db2"
        oracle = "oracle"
        odbc = "odbc"

    class Dbblocktype(Enum):
        """Enum for the Dbblocktype property."""

        usersize = "usersize"
        adaptivesize = "adaptivesize"

    class Fileblocktype(Enum):
        """Enum for the Fileblocktype property."""

        usersize = "usersize"
        adaptivesize = "adaptivesize"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class DsnType(Enum):
        """Enum for the DsnType property."""

        Snowflake = "Snowflake"
        DB2 = "DB2"
        Oracle = "Oracle"


class COLUMN_EXPORT:
    """Enums for properties in the COLUMN_EXPORT stage."""

    class Selection(Enum):
        """Enum for the Selection property."""

        file = "file"
        explicit = "explicit"

    class KeepExportedFields(Enum):
        """Enum for the KeepExportedFields property."""

        true = "keepExportedFields"
        false = " "

    class SaveRejects(Enum):
        """Enum for the SaveRejects property."""

        saveRejects = "saveRejects"
        custom = " "
        failRejects = "failRejects"

    class Type(Enum):
        """Enum for the Type property."""

        ustring = "ustring"
        string = "string"
        raw = "raw"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class FinalDelim(Enum):
        """Enum for the FinalDelim property."""

        custom = " "
        ws = "ws"
        end = "end"
        none = "none"
        null = "null"
        comma = "','"
        tab = "'\t'"

    class Fill(Enum):
        """Enum for the Fill property."""

        custom_fill_char = -1
        null = 0

    class CheckIntact(Enum):
        """Enum for the CheckIntact property."""

        check_intact = "check_intact"

    class RecordDelim(Enum):
        """Enum for the RecordDelim property."""

        custom = " "
        newline = "'\n'"
        null = "null"

    class RecordPrefix(Enum):
        """Enum for the RecordPrefix property."""

        one = 1
        two = 2
        four = 4

    class RecordLength(Enum):
        """Enum for the RecordLength property."""

        custom = " "
        fixed = "fixed"

    class RecordFormat(Enum):
        """Enum for the RecordFormat property."""

        type_implicit = "{type=implicit}"
        type_varying = "{type=varying}"
        type_varying_format_V = "{type=varying, format=V}"
        type_varying_format_VB = "{type=varying, format=VB}"
        type_varying_format_VBS = "{type=varying, format=VBS}"
        type_varying_format_VR = "{type=varying, format=VR}"
        type_varying_format_VS = "{type=varying, format=VS}"

    class Delim(Enum):
        """Enum for the Delim property."""

        custom = " "
        ws = "ws"
        end = "end"
        none = "none"
        null = "null"
        comma = "','"
        tab = "'\t'"

    class Quote(Enum):
        """Enum for the Quote property."""

        custom = " "
        single = "single"
        double = "double"
        none = "none"

    class NullFieldSep(Enum):
        """Enum for the NullFieldSep property."""

        space = " "
        comma = "','"

    class PrintField(Enum):
        """Enum for the PrintField property."""

        print_field = "print_field"

    class VectorPrefix(Enum):
        """Enum for the VectorPrefix property."""

        one = 1
        two = 2
        four = 4

    class Prefix(Enum):
        """Enum for the Prefix property."""

        one = 1
        two = 2
        four = 4

    class ByteOrder(Enum):
        """Enum for the ByteOrder property."""

        little_endian = "little_endian"
        big_endian = "big_endian"
        native_endian = "native_endian"

    class Charset(Enum):
        """Enum for the Charset property."""

        ebcdic = "ebcdic"
        ascii = "ascii"

    class DataFormat(Enum):
        """Enum for the DataFormat property."""

        binary = "binary"
        text = "text"

    class PadChar(Enum):
        """Enum for the PadChar property."""

        custom_pad_char = " "
        space = "' '"
        null = "null"

    class ExportEbcdicAsAscii(Enum):
        """Enum for the ExportEbcdicAsAscii property."""

        export_ebcdic_as_ascii = "export_ebcdic_as_ascii"

    class ImportAsciiAsEbcdic(Enum):
        """Enum for the ImportAsciiAsEbcdic property."""

        import_ascii_as_ebcdic = "import_ascii_as_ebcdic"

    class AllowAllZeros(Enum):
        """Enum for the AllowAllZeros property."""

        nofix_zero = "nofix_zero"
        fix_zero = "fix_zero"

    class DecimalSeparator(Enum):
        """Enum for the DecimalSeparator property."""

        custom = " "
        comma = "','"
        period = "'.'"

    class DecimalPacked(Enum):
        """Enum for the DecimalPacked property."""

        packed = "packed"
        separate = "separate"
        zoned = "zoned"
        overpunch = "overpunch"

    class DecimalPackedCheck(Enum):
        """Enum for the DecimalPackedCheck property."""

        check = "check"
        nocheck = "nocheck"

    class DecimalPackedSigned(Enum):
        """Enum for the DecimalPackedSigned property."""

        signed = "signed"
        unsigned = "unsigned"

    class AllowSignedImport(Enum):
        """Enum for the AllowSignedImport property."""

        allow_signed_import = "allow_signed_import"

    class DecimalPackedSignPosition(Enum):
        """Enum for the DecimalPackedSignPosition property."""

        trailing = "trailing"
        leading = "leading"

    class Round(Enum):
        """Enum for the Round property."""

        ceil = "ceil"
        floor = "floor"
        round_inf = "round_inf"
        trunc_zero = "trunc_zero"

    class IsJulian(Enum):
        """Enum for the IsJulian property."""

        julian = "julian"

    class IsMidnightSeconds(Enum):
        """Enum for the IsMidnightSeconds property."""

        midnight_seconds = "midnight_seconds"

    class RecLevelOption(Enum):
        """Enum for the RecLevelOption property."""

        final_delimiter = "final_delimiter"
        fill = "fill"
        final_delim_string = "final_delim_string"
        intact = "intact"
        record_delimiter = "record_delimiter"
        record_delim_string = "record_delim_string"
        record_length = "record_length"
        record_prefix = "record_prefix"
        record_format = "record_format"

    class FieldOption(Enum):
        """Enum for the FieldOption property."""

        delimiter = "delimiter"
        quote = "quote"
        actual_length = "actual_length"
        delim_string = "delim_string"
        null_length = "null_length"
        null_field = "null_field"
        prefix_bytes = "prefix_bytes"
        print_field = "print_field"
        vector_prefix = "vector_prefix"

    class GeneralOption(Enum):
        """Enum for the GeneralOption property."""

        byte_order = "byte_order"
        charset = "charset"
        data_format = "data_format"
        max_width = "max_width"
        field_width = "field_width"
        padchar = "padchar"

    class StringOption(Enum):
        """Enum for the StringOption property."""

        export_ebcdic_as_ascii = "export_ebcdic_as_ascii"
        import_ascii_as_ebcdic = "import_ascii_as_ebcdic"

    class DecimalOption(Enum):
        """Enum for the DecimalOption property."""

        allow_all_zeros = "allow_all_zeros"
        decimal_separator = "decimal_separator"
        decimal_packed = "decimal_packed"
        precision = "precision"
        round = "round"
        scale = "scale"

    class NumericOption(Enum):
        """Enum for the NumericOption property."""

        c_format = "c_format"
        in_format = "in_format"
        out_format = "out_format"

    class DateOption(Enum):
        """Enum for the DateOption property."""

        none = "none"
        days_since = "days_since"
        date_format = "date_format"
        is_julian = "is_julian"

    class TimeOption(Enum):
        """Enum for the TimeOption property."""

        none = "none"
        time_format = "time_format"
        is_midnight_seconds = "is_midnight_seconds"

    class TimestampOption(Enum):
        """Enum for the TimestampOption property."""

        none = "none"
        timestamp_format = "timestamp_format"


class SLOWLY_CHANGING_DIMENSION:
    """Enums for properties in the SLOWLY_CHANGING_DIMENSION stage."""

    class Keysourcetype(Enum):
        """Enum for the Keysourcetype property."""

        file = "file"
        dbsequence = "dbsequence"

    class Dbtype(Enum):
        """Enum for the Dbtype property."""

        db2 = "db2"
        oracle = "oracle"
        odbc = "odbc"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class Retrievekeys(Enum):
        """Enum for the Retrievekeys property."""

        in_blocks_of = "1"
        system_selected_block_size = "0"

    class OutputLinkField(Enum):
        """Enum for the OutputLinkField property."""

        custom = " "

    class DsnType(Enum):
        """Enum for the DsnType property."""

        Snowflake = "Snowflake"
        DB2 = "DB2"
        Oracle = "Oracle"

    class CollationSequence(Enum):
        """Enum for the CollationSequence property."""

        OFF = "OFF"
        af = "af"
        af_NA = "af_NA"
        af_ZA = "af_ZA"
        agq = "agq"
        agq_CM = "agq_CM"
        ak = "ak"
        ak_GH = "ak_GH"
        am = "am"
        am_ET = "am_ET"
        ar = "ar"
        ar_001 = "ar_001"
        ar_AE = "ar_AE"
        ar_BH = "ar_BH"
        ar_DJ = "ar_DJ"
        ar_DZ = "ar_DZ"
        ar_EG = "ar_EG"
        ar_EH = "ar_EH"
        ar_ER = "ar_ER"
        ar_IL = "ar_IL"
        ar_IQ = "ar_IQ"
        ar_JO = "ar_JO"
        ar_KM = "ar_KM"
        ar_KW = "ar_KW"
        ar_LB = "ar_LB"
        ar_LY = "ar_LY"
        ar_MA = "ar_MA"
        ar_MR = "ar_MR"
        ar_OM = "ar_OM"
        ar_PS = "ar_PS"
        ar_QA = "ar_QA"
        ar_SA = "ar_SA"
        ar_SD = "ar_SD"
        ar_SO = "ar_SO"
        ar_SY = "ar_SY"
        ar_TD = "ar_TD"
        ar_TN = "ar_TN"
        ar_YE = "ar_YE"
        as_ = "as"
        as_IN = "as_IN"
        asa = "asa"
        asa_TZ = "asa_TZ"
        az = "az"
        az_Cyrl = "az_Cyrl"
        az_Cyrl_AZ = "az_Cyrl_AZ"
        az_Latn = "az_Latn"
        az_Latn_AZ = "az_Latn_AZ"
        bas = "bas"
        bas_CM = "bas_CM"
        be = "be"
        be_BY = "be_BY"
        bem = "bem"
        bem_ZM = "bem_ZM"
        bez = "bez"
        bez_TZ = "bez_TZ"
        bg = "bg"
        bg_BG = "bg_BG"
        bm = "bm"
        bm_ML = "bm_ML"
        bn = "bn"
        bn_BD = "bn_BD"
        bn_IN = "bn_IN"
        bo = "bo"
        bo_CN = "bo_CN"
        bo_IN = "bo_IN"
        br = "br"
        br_FR = "br_FR"
        brx = "brx"
        brx_IN = "brx_IN"
        bs = "bs"
        bs_Cyrl = "bs_Cyrl"
        bs_Cyrl_BA = "bs_Cyrl_BA"
        bs_Latn = "bs_Latn"
        bs_Latn_BA = "bs_Latn_BA"
        ca = "ca"
        ca_AD = "ca_AD"
        ca_ES = "ca_ES"
        cgg = "cgg"
        cgg_UG = "cgg_UG"
        chr = "chr"
        chr_US = "chr_US"
        cs = "cs"
        cs_CZ = "cs_CZ"
        cy = "cy"
        cy_GB = "cy_GB"
        da = "da"
        da_DK = "da_DK"
        dav = "dav"
        dav_KE = "dav_KE"
        de = "de"
        de_AT = "de_AT"
        de_BE = "de_BE"
        de_CH = "de_CH"
        de_DE = "de_DE"
        de_LI = "de_LI"
        de_LU = "de_LU"
        dje = "dje"
        dje_NE = "dje_NE"
        dua = "dua"
        dua_CM = "dua_CM"
        dyo = "dyo"
        dyo_SN = "dyo_SN"
        dz = "dz"
        dz_BT = "dz_BT"
        ebu = "ebu"
        ebu_KE = "ebu_KE"
        ee = "ee"
        ee_GH = "ee_GH"
        ee_TG = "ee_TG"
        el = "el"
        el_CY = "el_CY"
        el_GR = "el_GR"
        en = "en"
        en_150 = "en_150"
        en_AG = "en_AG"
        en_AS = "en_AS"
        en_AU = "en_AU"
        en_BB = "en_BB"
        en_BE = "en_BE"
        en_BM = "en_BM"
        en_BS = "en_BS"
        en_BW = "en_BW"
        en_BZ = "en_BZ"
        en_CA = "en_CA"
        en_CM = "en_CM"
        en_DM = "en_DM"
        en_FJ = "en_FJ"
        en_FM = "en_FM"
        en_GB = "en_GB"
        en_GD = "en_GD"
        en_GG = "en_GG"
        en_GH = "en_GH"
        en_GI = "en_GI"
        en_GM = "en_GM"
        en_GU = "en_GU"
        en_GY = "en_GY"
        en_HK = "en_HK"
        en_IE = "en_IE"
        en_IM = "en_IM"
        en_IN = "en_IN"
        en_JE = "en_JE"
        en_JM = "en_JM"
        en_KE = "en_KE"
        en_KI = "en_KI"
        en_KN = "en_KN"
        en_KY = "en_KY"
        en_LC = "en_LC"
        en_LR = "en_LR"
        en_LS = "en_LS"
        en_MG = "en_MG"
        en_MH = "en_MH"
        en_MP = "en_MP"
        en_MT = "en_MT"
        en_MU = "en_MU"
        en_MW = "en_MW"
        en_NA = "en_NA"
        en_NG = "en_NG"
        en_NZ = "en_NZ"
        en_PG = "en_PG"
        en_PH = "en_PH"
        en_PK = "en_PK"
        en_PR = "en_PR"
        en_PW = "en_PW"
        en_SB = "en_SB"
        en_SC = "en_SC"
        en_SG = "en_SG"
        en_SL = "en_SL"
        en_SS = "en_SS"
        en_SZ = "en_SZ"
        en_TC = "en_TC"
        en_TO = "en_TO"
        en_TT = "en_TT"
        en_TZ = "en_TZ"
        en_UG = "en_UG"
        en_UM = "en_UM"
        en_US = "en_US"
        en_US_POSIX = "en_US_POSIX"
        en_VC = "en_VC"
        en_VG = "en_VG"
        en_VI = "en_VI"
        en_VU = "en_VU"
        en_WS = "en_WS"
        en_ZA = "en_ZA"
        en_ZM = "en_ZM"
        en_ZW = "en_ZW"
        eo = "eo"
        es = "es"
        es_419 = "es_419"
        es_AR = "es_AR"
        es_BO = "es_BO"
        es_CL = "es_CL"
        es_CO = "es_CO"
        es_CR = "es_CR"
        es_CU = "es_CU"
        es_DO = "es_DO"
        es_EA = "es_EA"
        es_EC = "es_EC"
        es_ES = "es_ES"
        es_GQ = "es_GQ"
        es_GT = "es_GT"
        es_HN = "es_HN"
        es_IC = "es_IC"
        es_MX = "es_MX"
        es_NI = "es_NI"
        es_PA = "es_PA"
        es_PE = "es_PE"
        es_PH = "es_PH"
        es_PR = "es_PR"
        es_PY = "es_PY"
        es_SV = "es_SV"
        es_US = "es_US"
        es_UY = "es_UY"
        es_VE = "es_VE"
        et = "et"
        et_EE = "et_EE"
        eu = "eu"
        eu_ES = "eu_ES"
        ewo = "ewo"
        ewo_CM = "ewo_CM"
        fa = "fa"
        fa_AF = "fa_AF"
        fa_IR = "fa_IR"
        ff = "ff"
        ff_SN = "ff_SN"
        fi = "fi"
        fi_FI = "fi_FI"
        fil = "fil"
        fil_PH = "fil_PH"
        fo = "fo"
        fo_FO = "fo_FO"
        fr = "fr"
        fr_BE = "fr_BE"
        fr_BF = "fr_BF"
        fr_BI = "fr_BI"
        fr_BJ = "fr_BJ"
        fr_BL = "fr_BL"
        fr_CA = "fr_CA"
        fr_CD = "fr_CD"
        fr_CF = "fr_CF"
        fr_CG = "fr_CG"
        fr_CH = "fr_CH"
        fr_CI = "fr_CI"
        fr_CM = "fr_CM"
        fr_DJ = "fr_DJ"
        fr_DZ = "fr_DZ"
        fr_FR = "fr_FR"
        fr_GA = "fr_GA"
        fr_GF = "fr_GF"
        fr_GN = "fr_GN"
        fr_GP = "fr_GP"
        fr_GQ = "fr_GQ"
        fr_HT = "fr_HT"
        fr_KM = "fr_KM"
        fr_LU = "fr_LU"
        fr_MA = "fr_MA"
        fr_MC = "fr_MC"
        fr_MF = "fr_MF"
        fr_MG = "fr_MG"
        fr_ML = "fr_ML"
        fr_MQ = "fr_MQ"
        fr_MR = "fr_MR"
        fr_MU = "fr_MU"
        fr_NC = "fr_NC"
        fr_NE = "fr_NE"
        fr_PF = "fr_PF"
        fr_RE = "fr_RE"
        fr_RW = "fr_RW"
        fr_SC = "fr_SC"
        fr_SN = "fr_SN"
        fr_SY = "fr_SY"
        fr_TD = "fr_TD"
        fr_TG = "fr_TG"
        fr_TN = "fr_TN"
        fr_VU = "fr_VU"
        fr_YT = "fr_YT"
        ga = "ga"
        ga_IE = "ga_IE"
        gl = "gl"
        gl_ES = "gl_ES"
        gsw = "gsw"
        gsw_CH = "gsw_CH"
        gu = "gu"
        gu_IN = "gu_IN"
        guz = "guz"
        guz_KE = "guz_KE"
        gv = "gv"
        gv_GB = "gv_GB"
        ha = "ha"
        ha_Latn = "ha_Latn"
        ha_Latn_GH = "ha_Latn_GH"
        ha_Latn_NE = "ha_Latn_NE"
        ha_Latn_NG = "ha_Latn_NG"
        haw = "haw"
        haw_US = "haw_US"
        he = "he"
        he_IL = "he_IL"
        hi = "hi"
        hi_IN = "hi_IN"
        hr = "hr"
        hr_BA = "hr_BA"
        hr_HR = "hr_HR"
        hu = "hu"
        hu_HU = "hu_HU"
        hy = "hy"
        hy_AM = "hy_AM"
        id = "id"
        id_ID = "id_ID"
        ig = "ig"
        ig_NG = "ig_NG"
        ii = "ii"
        ii_CN = "ii_CN"
        is_ = "is"
        is_IS = "is_IS"
        it = "it"
        it_CH = "it_CH"
        it_IT = "it_IT"
        it_SM = "it_SM"
        ja = "ja"
        ja_JP = "ja_JP"
        jgo = "jgo"
        jgo_CM = "jgo_CM"
        jmc = "jmc"
        jmc_TZ = "jmc_TZ"
        ka = "ka"
        ka_GE = "ka_GE"
        kab = "kab"
        kab_DZ = "kab_DZ"
        kam = "kam"
        kam_KE = "kam_KE"
        kde = "kde"
        kde_TZ = "kde_TZ"
        kea = "kea"
        kea_CV = "kea_CV"
        khq = "khq"
        khq_ML = "khq_ML"
        ki = "ki"
        ki_KE = "ki_KE"
        kk = "kk"
        kk_Cyrl = "kk_Cyrl"
        kk_Cyrl_KZ = "kk_Cyrl_KZ"
        kl = "kl"
        kl_GL = "kl_GL"
        kln = "kln"
        kln_KE = "kln_KE"
        km = "km"
        km_KH = "km_KH"
        kn = "kn"
        kn_IN = "kn_IN"
        ko = "ko"
        ko_KP = "ko_KP"
        ko_KR = "ko_KR"
        kok = "kok"
        kok_IN = "kok_IN"
        ks = "ks"
        ks_Arab = "ks_Arab"
        ks_Arab_IN = "ks_Arab_IN"
        ksb = "ksb"
        ksb_TZ = "ksb_TZ"
        ksf = "ksf"
        ksf_CM = "ksf_CM"
        kw = "kw"
        kw_GB = "kw_GB"
        lag = "lag"
        lag_TZ = "lag_TZ"
        lg = "lg"
        lg_UG = "lg_UG"
        ln = "ln"
        ln_AO = "ln_AO"
        ln_CD = "ln_CD"
        ln_CF = "ln_CF"
        ln_CG = "ln_CG"
        lo = "lo"
        lo_LA = "lo_LA"
        lt = "lt"
        lt_LT = "lt_LT"
        lu = "lu"
        lu_CD = "lu_CD"
        luo = "luo"
        luo_KE = "luo_KE"
        luy = "luy"
        luy_KE = "luy_KE"
        lv = "lv"
        lv_LV = "lv_LV"
        mas = "mas"
        mas_KE = "mas_KE"
        mas_TZ = "mas_TZ"
        mer = "mer"
        mer_KE = "mer_KE"
        mfe = "mfe"
        mfe_MU = "mfe_MU"
        mg = "mg"
        mg_MG = "mg_MG"
        mgh = "mgh"
        mgh_MZ = "mgh_MZ"
        mgo = "mgo"
        mgo_CM = "mgo_CM"
        mk = "mk"
        mk_MK = "mk_MK"
        ml = "ml"
        ml_IN = "ml_IN"
        mr = "mr"
        mr_IN = "mr_IN"
        ms = "ms"
        ms_BN = "ms_BN"
        ms_MY = "ms_MY"
        ms_SG = "ms_SG"
        mt = "mt"
        mt_MT = "mt_MT"
        mua = "mua"
        mua_CM = "mua_CM"
        my = "my"
        my_MM = "my_MM"
        naq = "naq"
        naq_NA = "naq_NA"
        nb = "nb"
        nb_NO = "nb_NO"
        nd = "nd"
        nd_ZW = "nd_ZW"
        ne = "ne"
        ne_IN = "ne_IN"
        ne_NP = "ne_NP"
        nl = "nl"
        nl_AW = "nl_AW"
        nl_BE = "nl_BE"
        nl_CW = "nl_CW"
        nl_NL = "nl_NL"
        nl_SR = "nl_SR"
        nl_SX = "nl_SX"
        nmg = "nmg"
        nmg_CM = "nmg_CM"
        nn = "nn"
        nn_NO = "nn_NO"
        nus = "nus"
        nus_SD = "nus_SD"
        nyn = "nyn"
        nyn_UG = "nyn_UG"
        om = "om"
        om_ET = "om_ET"
        om_KE = "om_KE"
        or_ = "or"
        or_IN = "or_IN"
        pa = "pa"
        pa_Arab = "pa_Arab"
        pa_Arab_PK = "pa_Arab_PK"
        pa_Guru = "pa_Guru"
        pa_Guru_IN = "pa_Guru_IN"
        pl = "pl"
        pl_PL = "pl_PL"
        ps = "ps"
        ps_AF = "ps_AF"
        pt = "pt"
        pt_AO = "pt_AO"
        pt_BR = "pt_BR"
        pt_CV = "pt_CV"
        pt_GW = "pt_GW"
        pt_MO = "pt_MO"
        pt_MZ = "pt_MZ"
        pt_PT = "pt_PT"
        pt_ST = "pt_ST"
        pt_TL = "pt_TL"
        rm = "rm"
        rm_CH = "rm_CH"
        rn = "rn"
        rn_BI = "rn_BI"
        ro = "ro"
        ro_MD = "ro_MD"
        ro_RO = "ro_RO"
        rof = "rof"
        rof_TZ = "rof_TZ"
        ru = "ru"
        ru_BY = "ru_BY"
        ru_KG = "ru_KG"
        ru_KZ = "ru_KZ"
        ru_MD = "ru_MD"
        ru_RU = "ru_RU"
        ru_UA = "ru_UA"
        rw = "rw"
        rw_RW = "rw_RW"
        rwk = "rwk"
        rwk_TZ = "rwk_TZ"
        saq = "saq"
        saq_KE = "saq_KE"
        sbp = "sbp"
        sbp_TZ = "sbp_TZ"
        seh = "seh"
        seh_MZ = "seh_MZ"
        ses = "ses"
        ses_ML = "ses_ML"
        sg = "sg"
        sg_CF = "sg_CF"
        shi = "shi"
        shi_Latn = "shi_Latn"
        shi_Latn_MA = "shi_Latn_MA"
        shi_Tfng = "shi_Tfng"
        shi_Tfng_MA = "shi_Tfng_MA"
        si = "si"
        si_LK = "si_LK"
        sk = "sk"
        sk_SK = "sk_SK"
        sl = "sl"
        sl_SI = "sl_SI"
        sn = "sn"
        sn_ZW = "sn_ZW"
        so = "so"
        so_DJ = "so_DJ"
        so_ET = "so_ET"
        so_KE = "so_KE"
        so_SO = "so_SO"
        sq = "sq"
        sq_AL = "sq_AL"
        sq_MK = "sq_MK"
        sr = "sr"
        sr_Cyrl = "sr_Cyrl"
        sr_Cyrl_BA = "sr_Cyrl_BA"
        sr_Cyrl_ME = "sr_Cyrl_ME"
        sr_Cyrl_RS = "sr_Cyrl_RS"
        sr_Latn = "sr_Latn"
        sr_Latn_BA = "sr_Latn_BA"
        sr_Latn_ME = "sr_Latn_ME"
        sr_Latn_RS = "sr_Latn_RS"
        sv = "sv"
        sv_AX = "sv_AX"
        sv_FI = "sv_FI"
        sv_SE = "sv_SE"
        sw = "sw"
        sw_KE = "sw_KE"
        sw_TZ = "sw_TZ"
        sw_UG = "sw_UG"
        swc = "swc"
        swc_CD = "swc_CD"
        ta = "ta"
        ta_IN = "ta_IN"
        ta_LK = "ta_LK"
        ta_MY = "ta_MY"
        ta_SG = "ta_SG"
        te = "te"
        te_IN = "te_IN"
        teo = "teo"
        teo_KE = "teo_KE"
        teo_UG = "teo_UG"
        th = "th"
        th_TH = "th_TH"
        ti = "ti"
        ti_ER = "ti_ER"
        ti_ET = "ti_ET"
        to = "to"
        to_TO = "to_TO"
        tr = "tr"
        tr_CY = "tr_CY"
        tr_TR = "tr_TR"
        twq = "twq"
        twq_NE = "twq_NE"
        tzm = "tzm"
        tzm_Latn = "tzm_Latn"
        tzm_Latn_MA = "tzm_Latn_MA"
        uk = "uk"
        uk_UA = "uk_UA"
        ur = "ur"
        ur_IN = "ur_IN"
        ur_PK = "ur_PK"
        uz = "uz"
        uz_Arab = "uz_Arab"
        uz_Arab_AF = "uz_Arab_AF"
        uz_Cyrl = "uz_Cyrl"
        uz_Cyrl_UZ = "uz_Cyrl_UZ"
        uz_Latn = "uz_Latn"
        uz_Latn_UZ = "uz_Latn_UZ"
        vai = "vai"
        vai_Latn = "vai_Latn"
        vai_Latn_LR = "vai_Latn_LR"
        vai_Vaii = "vai_Vaii"
        vai_Vaii_LR = "vai_Vaii_LR"
        vi = "vi"
        vi_VN = "vi_VN"
        vun = "vun"
        vun_TZ = "vun_TZ"
        xog = "xog"
        xog_UG = "xog_UG"
        yav = "yav"
        yav_CM = "yav_CM"
        yo = "yo"
        yo_NG = "yo_NG"
        zh = "zh"
        zh_Hans = "zh_Hans"
        zh_Hans_CN = "zh_Hans_CN"
        zh_Hans_HK = "zh_Hans_HK"
        zh_Hans_MO = "zh_Hans_MO"
        zh_Hans_SG = "zh_Hans_SG"
        zh_Hant = "zh_Hant"
        zh_Hant_HK = "zh_Hant_HK"
        zh_Hant_MO = "zh_Hant_MO"
        zh_Hant_TW = "zh_Hant_TW"
        zu = "zu"
        zu_ZA = "zu_ZA"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class COMPRESS:
    """Enums for properties in the COMPRESS stage."""

    class Command(Enum):
        """Enum for the Command property."""

        compress = "compress"
        gzip = "gzip"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_set = -2
        clear = 0
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class COLUMN_IMPORT:
    """Enums for properties in the COLUMN_IMPORT stage."""

    class SaveRejectsFailRejects(Enum):
        """Enum for the SaveRejectsFailRejects property."""

        saveRejects = "saveRejects"
        warn = " "
        failRejects = "failRejects"

    class Fields(Enum):
        """Enum for the Fields property."""

        custom = " "

    class Selection(Enum):
        """Enum for the Selection property."""

        file = "file"
        explicit = "explicit"

    class KeepField(Enum):
        """Enum for the KeepField property."""

        true = "keepField"
        false = " "

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class FinalDelim(Enum):
        """Enum for the FinalDelim property."""

        custom = " "
        ws = "ws"
        end = "end"
        none = "none"
        null = "null"
        comma = "','"
        tab = "'\t'"

    class Fill(Enum):
        """Enum for the Fill property."""

        custom_fill_char = -1
        null = 0

    class CheckIntact(Enum):
        """Enum for the CheckIntact property."""

        check_intact = "check_intact"

    class RecordDelim(Enum):
        """Enum for the RecordDelim property."""

        custom = " "
        newline = "'\n'"
        null = "null"

    class RecordPrefix(Enum):
        """Enum for the RecordPrefix property."""

        one = 1
        two = 2
        four = 4

    class RecordLength(Enum):
        """Enum for the RecordLength property."""

        custom = " "
        fixed = "fixed"

    class RecordFormat(Enum):
        """Enum for the RecordFormat property."""

        type_implicit = "{type=implicit}"
        type_varying = "{type=varying}"
        type_varying_format_V = "{type=varying, format=V}"
        type_varying_format_VB = "{type=varying, format=VB}"
        type_varying_format_VBS = "{type=varying, format=VBS}"
        type_varying_format_VR = "{type=varying, format=VR}"
        type_varying_format_VS = "{type=varying, format=VS}"

    class Delim(Enum):
        """Enum for the Delim property."""

        custom = " "
        ws = "ws"
        end = "end"
        none = "none"
        null = "null"
        comma = "','"
        tab = "'\t'"

    class Quote(Enum):
        """Enum for the Quote property."""

        custom = " "
        single = "single"
        double = "double"
        none = "none"

    class NullFieldSep(Enum):
        """Enum for the NullFieldSep property."""

        space = " "
        comma = "','"

    class PrintField(Enum):
        """Enum for the PrintField property."""

        print_field = "print_field"

    class VectorPrefix(Enum):
        """Enum for the VectorPrefix property."""

        one = 1
        two = 2
        four = 4

    class Prefix(Enum):
        """Enum for the Prefix property."""

        one = 1
        two = 2
        four = 4

    class ByteOrder(Enum):
        """Enum for the ByteOrder property."""

        little_endian = "little_endian"
        big_endian = "big_endian"
        native_endian = "native_endian"

    class Charset(Enum):
        """Enum for the Charset property."""

        ebcdic = "ebcdic"
        ascii = "ascii"

    class DataFormat(Enum):
        """Enum for the DataFormat property."""

        binary = "binary"
        text = "text"

    class Padchar(Enum):
        """Enum for the Padchar property."""

        custom = " "
        false_ = "' '"
        null = "null"

    class ExportEbcdicAsAscii(Enum):
        """Enum for the ExportEbcdicAsAscii property."""

        export_ebcdic_as_ascii = "export_ebcdic_as_ascii"

    class ImportAsciiAsEbcdic(Enum):
        """Enum for the ImportAsciiAsEbcdic property."""

        import_ascii_as_ebcdic = "import_ascii_as_ebcdic"

    class AllowAllZeros(Enum):
        """Enum for the AllowAllZeros property."""

        nofix_zero = "nofix_zero"
        fix_zero = "fix_zero"

    class DecimalSeparator(Enum):
        """Enum for the DecimalSeparator property."""

        custom = " "
        comma = "','"
        period = "'.'"

    class DecimalPacked(Enum):
        """Enum for the DecimalPacked property."""

        packed = "packed"
        separate = "separate"
        zoned = "zoned"
        overpunch = "overpunch"

    class DecimalPackedCheck(Enum):
        """Enum for the DecimalPackedCheck property."""

        check = "check"
        nocheck = "nocheck"

    class DecimalPackedSigned(Enum):
        """Enum for the DecimalPackedSigned property."""

        signed = "signed"
        unsigned = "unsigned"

    class AllowSignedImport(Enum):
        """Enum for the AllowSignedImport property."""

        allow_signed_import = "allow_signed_import"

    class DecimalPackedSignPosition(Enum):
        """Enum for the DecimalPackedSignPosition property."""

        trailing = "trailing"
        leading = "leading"

    class Round(Enum):
        """Enum for the Round property."""

        ceil = "ceil"
        floor = "floor"
        round_inf = "round_inf"
        trunc_zero = "trunc_zero"

    class IsJulian(Enum):
        """Enum for the IsJulian property."""

        julian = "julian"

    class IsMidnightSeconds(Enum):
        """Enum for the IsMidnightSeconds property."""

        midnight_seconds = "midnight_seconds"

    class RecLevelOption(Enum):
        """Enum for the RecLevelOption property."""

        final_delimiter = "final_delimiter"
        fill = "fill"
        final_delim_string = "final_delim_string"
        intact = "intact"
        record_delimiter = "record_delimiter"
        record_delim_string = "record_delim_string"
        record_length = "record_length"
        record_prefix = "record_prefix"
        record_format = "record_format"

    class FieldOption(Enum):
        """Enum for the FieldOption property."""

        delimiter = "delimiter"
        quote = "quote"
        actual_length = "actual_length"
        delim_string = "delim_string"
        null_length = "null_length"
        null_field = "null_field"
        prefix_bytes = "prefix_bytes"
        print_field = "print_field"
        vector_prefix = "vector_prefix"

    class GeneralOption(Enum):
        """Enum for the GeneralOption property."""

        byte_order = "byte_order"
        charset = "charset"
        data_format = "data_format"
        max_width = "max_width"
        field_width = "field_width"
        padchar = "padchar"

    class StringOption(Enum):
        """Enum for the StringOption property."""

        export_ebcdic_as_ascii = "export_ebcdic_as_ascii"
        import_ascii_as_ebcdic = "import_ascii_as_ebcdic"

    class DecimalOption(Enum):
        """Enum for the DecimalOption property."""

        allow_all_zeros = "allow_all_zeros"
        decimal_separator = "decimal_separator"
        decimal_packed = "decimal_packed"
        precision = "precision"
        round = "round"
        scale = "scale"

    class NumericOption(Enum):
        """Enum for the NumericOption property."""

        c_format = "c_format"
        in_format = "in_format"
        out_format = "out_format"

    class DateOption(Enum):
        """Enum for the DateOption property."""

        none = "none"
        days_since = "days_since"
        date_format = "date_format"
        is_julian = "is_julian"

    class TimeOption(Enum):
        """Enum for the TimeOption property."""

        none = "none"
        time_format = "time_format"
        is_midnight_seconds = "is_midnight_seconds"

    class TimestampOption(Enum):
        """Enum for the TimestampOption property."""

        none = "none"
        timestamp_format = "timestamp_format"


class SAPBAPI:
    """Enums for properties in the SAPBAPI stage."""

    class Force(Enum):
        """Enum for the Force property."""

        false = " "
        true = "force"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class TAIL:
    """Enums for properties in the TAIL stage."""

    class Selection(Enum):
        """Enum for the Selection property."""

        true = " "
        false = "part"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class EXTERNAL_FILTER:
    """Enums for properties in the EXTERNAL_FILTER stage."""

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_seq = "default_seq"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class FUNNEL:
    """Enums for properties in the FUNNEL stage."""

    class Operator(Enum):
        """Enum for the Operator property."""

        sortfunnel = "sortfunnel"
        sequence = "sequence"
        funnel = "funnel"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class CollationSequence(Enum):
        """Enum for the CollationSequence property."""

        OFF = "OFF"
        af = "af"
        af_NA = "af_NA"
        af_ZA = "af_ZA"
        agq = "agq"
        agq_CM = "agq_CM"
        ak = "ak"
        ak_GH = "ak_GH"
        am = "am"
        am_ET = "am_ET"
        ar = "ar"
        ar_001 = "ar_001"
        ar_AE = "ar_AE"
        ar_BH = "ar_BH"
        ar_DJ = "ar_DJ"
        ar_DZ = "ar_DZ"
        ar_EG = "ar_EG"
        ar_EH = "ar_EH"
        ar_ER = "ar_ER"
        ar_IL = "ar_IL"
        ar_IQ = "ar_IQ"
        ar_JO = "ar_JO"
        ar_KM = "ar_KM"
        ar_KW = "ar_KW"
        ar_LB = "ar_LB"
        ar_LY = "ar_LY"
        ar_MA = "ar_MA"
        ar_MR = "ar_MR"
        ar_OM = "ar_OM"
        ar_PS = "ar_PS"
        ar_QA = "ar_QA"
        ar_SA = "ar_SA"
        ar_SD = "ar_SD"
        ar_SO = "ar_SO"
        ar_SY = "ar_SY"
        ar_TD = "ar_TD"
        ar_TN = "ar_TN"
        ar_YE = "ar_YE"
        as_ = "as"
        as_IN = "as_IN"
        asa = "asa"
        asa_TZ = "asa_TZ"
        az = "az"
        az_Cyrl = "az_Cyrl"
        az_Cyrl_AZ = "az_Cyrl_AZ"
        az_Latn = "az_Latn"
        az_Latn_AZ = "az_Latn_AZ"
        bas = "bas"
        bas_CM = "bas_CM"
        be = "be"
        be_BY = "be_BY"
        bem = "bem"
        bem_ZM = "bem_ZM"
        bez = "bez"
        bez_TZ = "bez_TZ"
        bg = "bg"
        bg_BG = "bg_BG"
        bm = "bm"
        bm_ML = "bm_ML"
        bn = "bn"
        bn_BD = "bn_BD"
        bn_IN = "bn_IN"
        bo = "bo"
        bo_CN = "bo_CN"
        bo_IN = "bo_IN"
        br = "br"
        br_FR = "br_FR"
        brx = "brx"
        brx_IN = "brx_IN"
        bs = "bs"
        bs_Cyrl = "bs_Cyrl"
        bs_Cyrl_BA = "bs_Cyrl_BA"
        bs_Latn = "bs_Latn"
        bs_Latn_BA = "bs_Latn_BA"
        ca = "ca"
        ca_AD = "ca_AD"
        ca_ES = "ca_ES"
        cgg = "cgg"
        cgg_UG = "cgg_UG"
        chr = "chr"
        chr_US = "chr_US"
        cs = "cs"
        cs_CZ = "cs_CZ"
        cy = "cy"
        cy_GB = "cy_GB"
        da = "da"
        da_DK = "da_DK"
        dav = "dav"
        dav_KE = "dav_KE"
        de = "de"
        de_AT = "de_AT"
        de_BE = "de_BE"
        de_CH = "de_CH"
        de_DE = "de_DE"
        de_LI = "de_LI"
        de_LU = "de_LU"
        dje = "dje"
        dje_NE = "dje_NE"
        dua = "dua"
        dua_CM = "dua_CM"
        dyo = "dyo"
        dyo_SN = "dyo_SN"
        dz = "dz"
        dz_BT = "dz_BT"
        ebu = "ebu"
        ebu_KE = "ebu_KE"
        ee = "ee"
        ee_GH = "ee_GH"
        ee_TG = "ee_TG"
        el = "el"
        el_CY = "el_CY"
        el_GR = "el_GR"
        en = "en"
        en_150 = "en_150"
        en_AG = "en_AG"
        en_AS = "en_AS"
        en_AU = "en_AU"
        en_BB = "en_BB"
        en_BE = "en_BE"
        en_BM = "en_BM"
        en_BS = "en_BS"
        en_BW = "en_BW"
        en_BZ = "en_BZ"
        en_CA = "en_CA"
        en_CM = "en_CM"
        en_DM = "en_DM"
        en_FJ = "en_FJ"
        en_FM = "en_FM"
        en_GB = "en_GB"
        en_GD = "en_GD"
        en_GG = "en_GG"
        en_GH = "en_GH"
        en_GI = "en_GI"
        en_GM = "en_GM"
        en_GU = "en_GU"
        en_GY = "en_GY"
        en_HK = "en_HK"
        en_IE = "en_IE"
        en_IM = "en_IM"
        en_IN = "en_IN"
        en_JE = "en_JE"
        en_JM = "en_JM"
        en_KE = "en_KE"
        en_KI = "en_KI"
        en_KN = "en_KN"
        en_KY = "en_KY"
        en_LC = "en_LC"
        en_LR = "en_LR"
        en_LS = "en_LS"
        en_MG = "en_MG"
        en_MH = "en_MH"
        en_MP = "en_MP"
        en_MT = "en_MT"
        en_MU = "en_MU"
        en_MW = "en_MW"
        en_NA = "en_NA"
        en_NG = "en_NG"
        en_NZ = "en_NZ"
        en_PG = "en_PG"
        en_PH = "en_PH"
        en_PK = "en_PK"
        en_PR = "en_PR"
        en_PW = "en_PW"
        en_SB = "en_SB"
        en_SC = "en_SC"
        en_SG = "en_SG"
        en_SL = "en_SL"
        en_SS = "en_SS"
        en_SZ = "en_SZ"
        en_TC = "en_TC"
        en_TO = "en_TO"
        en_TT = "en_TT"
        en_TZ = "en_TZ"
        en_UG = "en_UG"
        en_UM = "en_UM"
        en_US = "en_US"
        en_US_POSIX = "en_US_POSIX"
        en_VC = "en_VC"
        en_VG = "en_VG"
        en_VI = "en_VI"
        en_VU = "en_VU"
        en_WS = "en_WS"
        en_ZA = "en_ZA"
        en_ZM = "en_ZM"
        en_ZW = "en_ZW"
        eo = "eo"
        es = "es"
        es_419 = "es_419"
        es_AR = "es_AR"
        es_BO = "es_BO"
        es_CL = "es_CL"
        es_CO = "es_CO"
        es_CR = "es_CR"
        es_CU = "es_CU"
        es_DO = "es_DO"
        es_EA = "es_EA"
        es_EC = "es_EC"
        es_ES = "es_ES"
        es_GQ = "es_GQ"
        es_GT = "es_GT"
        es_HN = "es_HN"
        es_IC = "es_IC"
        es_MX = "es_MX"
        es_NI = "es_NI"
        es_PA = "es_PA"
        es_PE = "es_PE"
        es_PH = "es_PH"
        es_PR = "es_PR"
        es_PY = "es_PY"
        es_SV = "es_SV"
        es_US = "es_US"
        es_UY = "es_UY"
        es_VE = "es_VE"
        et = "et"
        et_EE = "et_EE"
        eu = "eu"
        eu_ES = "eu_ES"
        ewo = "ewo"
        ewo_CM = "ewo_CM"
        fa = "fa"
        fa_AF = "fa_AF"
        fa_IR = "fa_IR"
        ff = "ff"
        ff_SN = "ff_SN"
        fi = "fi"
        fi_FI = "fi_FI"
        fil = "fil"
        fil_PH = "fil_PH"
        fo = "fo"
        fo_FO = "fo_FO"
        fr = "fr"
        fr_BE = "fr_BE"
        fr_BF = "fr_BF"
        fr_BI = "fr_BI"
        fr_BJ = "fr_BJ"
        fr_BL = "fr_BL"
        fr_CA = "fr_CA"
        fr_CD = "fr_CD"
        fr_CF = "fr_CF"
        fr_CG = "fr_CG"
        fr_CH = "fr_CH"
        fr_CI = "fr_CI"
        fr_CM = "fr_CM"
        fr_DJ = "fr_DJ"
        fr_DZ = "fr_DZ"
        fr_FR = "fr_FR"
        fr_GA = "fr_GA"
        fr_GF = "fr_GF"
        fr_GN = "fr_GN"
        fr_GP = "fr_GP"
        fr_GQ = "fr_GQ"
        fr_HT = "fr_HT"
        fr_KM = "fr_KM"
        fr_LU = "fr_LU"
        fr_MA = "fr_MA"
        fr_MC = "fr_MC"
        fr_MF = "fr_MF"
        fr_MG = "fr_MG"
        fr_ML = "fr_ML"
        fr_MQ = "fr_MQ"
        fr_MR = "fr_MR"
        fr_MU = "fr_MU"
        fr_NC = "fr_NC"
        fr_NE = "fr_NE"
        fr_PF = "fr_PF"
        fr_RE = "fr_RE"
        fr_RW = "fr_RW"
        fr_SC = "fr_SC"
        fr_SN = "fr_SN"
        fr_SY = "fr_SY"
        fr_TD = "fr_TD"
        fr_TG = "fr_TG"
        fr_TN = "fr_TN"
        fr_VU = "fr_VU"
        fr_YT = "fr_YT"
        ga = "ga"
        ga_IE = "ga_IE"
        gl = "gl"
        gl_ES = "gl_ES"
        gsw = "gsw"
        gsw_CH = "gsw_CH"
        gu = "gu"
        gu_IN = "gu_IN"
        guz = "guz"
        guz_KE = "guz_KE"
        gv = "gv"
        gv_GB = "gv_GB"
        ha = "ha"
        ha_Latn = "ha_Latn"
        ha_Latn_GH = "ha_Latn_GH"
        ha_Latn_NE = "ha_Latn_NE"
        ha_Latn_NG = "ha_Latn_NG"
        haw = "haw"
        haw_US = "haw_US"
        he = "he"
        he_IL = "he_IL"
        hi = "hi"
        hi_IN = "hi_IN"
        hr = "hr"
        hr_BA = "hr_BA"
        hr_HR = "hr_HR"
        hu = "hu"
        hu_HU = "hu_HU"
        hy = "hy"
        hy_AM = "hy_AM"
        id = "id"
        id_ID = "id_ID"
        ig = "ig"
        ig_NG = "ig_NG"
        ii = "ii"
        ii_CN = "ii_CN"
        is_ = "is"
        is_IS = "is_IS"
        it = "it"
        it_CH = "it_CH"
        it_IT = "it_IT"
        it_SM = "it_SM"
        ja = "ja"
        ja_JP = "ja_JP"
        jgo = "jgo"
        jgo_CM = "jgo_CM"
        jmc = "jmc"
        jmc_TZ = "jmc_TZ"
        ka = "ka"
        ka_GE = "ka_GE"
        kab = "kab"
        kab_DZ = "kab_DZ"
        kam = "kam"
        kam_KE = "kam_KE"
        kde = "kde"
        kde_TZ = "kde_TZ"
        kea = "kea"
        kea_CV = "kea_CV"
        khq = "khq"
        khq_ML = "khq_ML"
        ki = "ki"
        ki_KE = "ki_KE"
        kk = "kk"
        kk_Cyrl = "kk_Cyrl"
        kk_Cyrl_KZ = "kk_Cyrl_KZ"
        kl = "kl"
        kl_GL = "kl_GL"
        kln = "kln"
        kln_KE = "kln_KE"
        km = "km"
        km_KH = "km_KH"
        kn = "kn"
        kn_IN = "kn_IN"
        ko = "ko"
        ko_KP = "ko_KP"
        ko_KR = "ko_KR"
        kok = "kok"
        kok_IN = "kok_IN"
        ks = "ks"
        ks_Arab = "ks_Arab"
        ks_Arab_IN = "ks_Arab_IN"
        ksb = "ksb"
        ksb_TZ = "ksb_TZ"
        ksf = "ksf"
        ksf_CM = "ksf_CM"
        kw = "kw"
        kw_GB = "kw_GB"
        lag = "lag"
        lag_TZ = "lag_TZ"
        lg = "lg"
        lg_UG = "lg_UG"
        ln = "ln"
        ln_AO = "ln_AO"
        ln_CD = "ln_CD"
        ln_CF = "ln_CF"
        ln_CG = "ln_CG"
        lo = "lo"
        lo_LA = "lo_LA"
        lt = "lt"
        lt_LT = "lt_LT"
        lu = "lu"
        lu_CD = "lu_CD"
        luo = "luo"
        luo_KE = "luo_KE"
        luy = "luy"
        luy_KE = "luy_KE"
        lv = "lv"
        lv_LV = "lv_LV"
        mas = "mas"
        mas_KE = "mas_KE"
        mas_TZ = "mas_TZ"
        mer = "mer"
        mer_KE = "mer_KE"
        mfe = "mfe"
        mfe_MU = "mfe_MU"
        mg = "mg"
        mg_MG = "mg_MG"
        mgh = "mgh"
        mgh_MZ = "mgh_MZ"
        mgo = "mgo"
        mgo_CM = "mgo_CM"
        mk = "mk"
        mk_MK = "mk_MK"
        ml = "ml"
        ml_IN = "ml_IN"
        mr = "mr"
        mr_IN = "mr_IN"
        ms = "ms"
        ms_BN = "ms_BN"
        ms_MY = "ms_MY"
        ms_SG = "ms_SG"
        mt = "mt"
        mt_MT = "mt_MT"
        mua = "mua"
        mua_CM = "mua_CM"
        my = "my"
        my_MM = "my_MM"
        naq = "naq"
        naq_NA = "naq_NA"
        nb = "nb"
        nb_NO = "nb_NO"
        nd = "nd"
        nd_ZW = "nd_ZW"
        ne = "ne"
        ne_IN = "ne_IN"
        ne_NP = "ne_NP"
        nl = "nl"
        nl_AW = "nl_AW"
        nl_BE = "nl_BE"
        nl_CW = "nl_CW"
        nl_NL = "nl_NL"
        nl_SR = "nl_SR"
        nl_SX = "nl_SX"
        nmg = "nmg"
        nmg_CM = "nmg_CM"
        nn = "nn"
        nn_NO = "nn_NO"
        nus = "nus"
        nus_SD = "nus_SD"
        nyn = "nyn"
        nyn_UG = "nyn_UG"
        om = "om"
        om_ET = "om_ET"
        om_KE = "om_KE"
        or_ = "or"
        or_IN = "or_IN"
        pa = "pa"
        pa_Arab = "pa_Arab"
        pa_Arab_PK = "pa_Arab_PK"
        pa_Guru = "pa_Guru"
        pa_Guru_IN = "pa_Guru_IN"
        pl = "pl"
        pl_PL = "pl_PL"
        ps = "ps"
        ps_AF = "ps_AF"
        pt = "pt"
        pt_AO = "pt_AO"
        pt_BR = "pt_BR"
        pt_CV = "pt_CV"
        pt_GW = "pt_GW"
        pt_MO = "pt_MO"
        pt_MZ = "pt_MZ"
        pt_PT = "pt_PT"
        pt_ST = "pt_ST"
        pt_TL = "pt_TL"
        rm = "rm"
        rm_CH = "rm_CH"
        rn = "rn"
        rn_BI = "rn_BI"
        ro = "ro"
        ro_MD = "ro_MD"
        ro_RO = "ro_RO"
        rof = "rof"
        rof_TZ = "rof_TZ"
        ru = "ru"
        ru_BY = "ru_BY"
        ru_KG = "ru_KG"
        ru_KZ = "ru_KZ"
        ru_MD = "ru_MD"
        ru_RU = "ru_RU"
        ru_UA = "ru_UA"
        rw = "rw"
        rw_RW = "rw_RW"
        rwk = "rwk"
        rwk_TZ = "rwk_TZ"
        saq = "saq"
        saq_KE = "saq_KE"
        sbp = "sbp"
        sbp_TZ = "sbp_TZ"
        seh = "seh"
        seh_MZ = "seh_MZ"
        ses = "ses"
        ses_ML = "ses_ML"
        sg = "sg"
        sg_CF = "sg_CF"
        shi = "shi"
        shi_Latn = "shi_Latn"
        shi_Latn_MA = "shi_Latn_MA"
        shi_Tfng = "shi_Tfng"
        shi_Tfng_MA = "shi_Tfng_MA"
        si = "si"
        si_LK = "si_LK"
        sk = "sk"
        sk_SK = "sk_SK"
        sl = "sl"
        sl_SI = "sl_SI"
        sn = "sn"
        sn_ZW = "sn_ZW"
        so = "so"
        so_DJ = "so_DJ"
        so_ET = "so_ET"
        so_KE = "so_KE"
        so_SO = "so_SO"
        sq = "sq"
        sq_AL = "sq_AL"
        sq_MK = "sq_MK"
        sr = "sr"
        sr_Cyrl = "sr_Cyrl"
        sr_Cyrl_BA = "sr_Cyrl_BA"
        sr_Cyrl_ME = "sr_Cyrl_ME"
        sr_Cyrl_RS = "sr_Cyrl_RS"
        sr_Latn = "sr_Latn"
        sr_Latn_BA = "sr_Latn_BA"
        sr_Latn_ME = "sr_Latn_ME"
        sr_Latn_RS = "sr_Latn_RS"
        sv = "sv"
        sv_AX = "sv_AX"
        sv_FI = "sv_FI"
        sv_SE = "sv_SE"
        sw = "sw"
        sw_KE = "sw_KE"
        sw_TZ = "sw_TZ"
        sw_UG = "sw_UG"
        swc = "swc"
        swc_CD = "swc_CD"
        ta = "ta"
        ta_IN = "ta_IN"
        ta_LK = "ta_LK"
        ta_MY = "ta_MY"
        ta_SG = "ta_SG"
        te = "te"
        te_IN = "te_IN"
        teo = "teo"
        teo_KE = "teo_KE"
        teo_UG = "teo_UG"
        th = "th"
        th_TH = "th_TH"
        ti = "ti"
        ti_ER = "ti_ER"
        ti_ET = "ti_ET"
        to = "to"
        to_TO = "to_TO"
        tr = "tr"
        tr_CY = "tr_CY"
        tr_TR = "tr_TR"
        twq = "twq"
        twq_NE = "twq_NE"
        tzm = "tzm"
        tzm_Latn = "tzm_Latn"
        tzm_Latn_MA = "tzm_Latn_MA"
        uk = "uk"
        uk_UA = "uk_UA"
        ur = "ur"
        ur_IN = "ur_IN"
        ur_PK = "ur_PK"
        uz = "uz"
        uz_Arab = "uz_Arab"
        uz_Arab_AF = "uz_Arab_AF"
        uz_Cyrl = "uz_Cyrl"
        uz_Cyrl_UZ = "uz_Cyrl_UZ"
        uz_Latn = "uz_Latn"
        uz_Latn_UZ = "uz_Latn_UZ"
        vai = "vai"
        vai_Latn = "vai_Latn"
        vai_Latn_LR = "vai_Latn_LR"
        vai_Vaii = "vai_Vaii"
        vai_Vaii_LR = "vai_Vaii_LR"
        vi = "vi"
        vi_VN = "vi_VN"
        vun = "vun"
        vun_TZ = "vun_TZ"
        xog = "xog"
        xog_UG = "xog_UG"
        yav = "yav"
        yav_CM = "yav_CM"
        yo = "yo"
        yo_NG = "yo_NG"
        zh = "zh"
        zh_Hans = "zh_Hans"
        zh_Hans_CN = "zh_Hans_CN"
        zh_Hans_HK = "zh_Hans_HK"
        zh_Hans_MO = "zh_Hans_MO"
        zh_Hans_SG = "zh_Hans_SG"
        zh_Hant = "zh_Hant"
        zh_Hant_HK = "zh_Hant_HK"
        zh_Hant_MO = "zh_Hant_MO"
        zh_Hant_TW = "zh_Hant_TW"
        zu = "zu"
        zu_ZA = "zu_ZA"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class STANDARDIZE:
    """Enums for properties in the STANDARDIZE stage."""

    class Case(Enum):
        """Enum for the Case property."""

        UPPERALL = "UPPERALL"
        PRESERVE = "PRESERVE"
        LOWERALL = "LOWERALL"
        UPPEREACHWORD = "UPPEREACHWORD"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        db2part = "db2part"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class Db2NameSelect(Enum):
        """Enum for the Db2NameSelect property."""

        use_db2NameEnv = "use_db2NameEnv"
        use_userDefinedName = "use_userDefinedName"

    class Db2InstanceSelect(Enum):
        """Enum for the Db2InstanceSelect property."""

        use_db2InstanceEnv = "use_db2InstanceEnv"
        use_userDefinedInstance = "use_userDefinedInstance"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        Select_a_column = "Select a column"


class EXPAND:
    """Enums for properties in the EXPAND stage."""

    class Command(Enum):
        """Enum for the Command property."""

        gzip = "gzip"
        compress = "compress"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class LOOKUPFILESET:
    """Enums for properties in the LOOKUPFILESET stage."""

    class AllowDups(Enum):
        """Enum for the AllowDups property."""

        true = "allow_dups"
        false = " "

    class Range(Enum):
        """Enum for the Range property."""

        false = " "
        true = "range"

    class KeyLowKeep(Enum):
        """Enum for the KeyLowKeep property."""

        true = "keep"
        false = " "

    class KeyLowCiCs(Enum):
        """Enum for the KeyLowCiCs property."""

        cs = "cs"
        ci = "ci"

    class KeyHighKeep(Enum):
        """Enum for the KeyHighKeep property."""

        true = "keep"
        false = " "

    class KeyHighCiCs(Enum):
        """Enum for the KeyHighCiCs property."""

        cs = "cs"
        ci = "ci"

    class KeyOrderedKeep(Enum):
        """Enum for the KeyOrderedKeep property."""

        true = "keep"
        false = " "

    class KeyOrderedCiCs(Enum):
        """Enum for the KeyOrderedCiCs property."""

        cs = "cs"
        ci = "ci"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class BLOOM_FILTER:
    """Enums for properties in the BLOOM_FILTER stage."""

    class Selection(Enum):
        """Enum for the Selection property."""

        create = "create"
        process = "process"

    class FlagColumn(Enum):
        """Enum for the FlagColumn property."""

        false = " "
        true = "flag_column"

    class DropOld(Enum):
        """Enum for the DropOld property."""

        false = " "
        true = "drop_old"

    class Truncate(Enum):
        """Enum for the Truncate property."""

        false = " "
        true = "truncate"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class HEAD:
    """Enums for properties in the HEAD stage."""

    class All(Enum):
        """Enum for the All property."""

        false = " "
        true = "all"

    class Selection(Enum):
        """Enum for the Selection property."""

        false = "part"
        true = " "

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class ROW_GENERATOR:
    """Enums for properties in the ROW_GENERATOR stage."""

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_seq = "default_seq"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class CHANGE_CAPTURE:
    """Enums for properties in the CHANGE_CAPTURE stage."""

    class Selection(Enum):
        """Enum for the Selection property."""

        allkeys = "allkeys"
        custom = " "
        allvalues = "allvalues"

    class SelectionCiCs(Enum):
        """Enum for the SelectionCiCs property."""

        cs = "cs"
        ci = "ci"

    class SelectionAscDesc(Enum):
        """Enum for the SelectionAscDesc property."""

        desc = "desc"
        asc = "asc"

    class SelectionNulls(Enum):
        """Enum for the SelectionNulls property."""

        last = "last"
        first = "first"

    class DoStats(Enum):
        """Enum for the DoStats property."""

        true = "doStats"
        false = " "

    class KeepInsertDropInsert(Enum):
        """Enum for the KeepInsertDropInsert property."""

        dropInsert = "dropInsert"
        keepInsert = "keepInsert"

    class KeepDeleteDropDelete(Enum):
        """Enum for the KeepDeleteDropDelete property."""

        dropDelete = "dropDelete"
        keepDelete = "keepDelete"

    class KeepEditDropEdit(Enum):
        """Enum for the KeepEditDropEdit property."""

        dropEdit = "dropEdit"
        keepEdit = "keepEdit"

    class KeepCopyDropCopy(Enum):
        """Enum for the KeepCopyDropCopy property."""

        dropCopy = "dropCopy"
        keepCopy = "keepCopy"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_set = -2
        clear = 0
        set = 1

    class CollationSequence(Enum):
        """Enum for the CollationSequence property."""

        OFF = "OFF"
        af = "af"
        af_NA = "af_NA"
        af_ZA = "af_ZA"
        agq = "agq"
        agq_CM = "agq_CM"
        ak = "ak"
        ak_GH = "ak_GH"
        am = "am"
        am_ET = "am_ET"
        ar = "ar"
        ar_001 = "ar_001"
        ar_AE = "ar_AE"
        ar_BH = "ar_BH"
        ar_DJ = "ar_DJ"
        ar_DZ = "ar_DZ"
        ar_EG = "ar_EG"
        ar_EH = "ar_EH"
        ar_ER = "ar_ER"
        ar_IL = "ar_IL"
        ar_IQ = "ar_IQ"
        ar_JO = "ar_JO"
        ar_KM = "ar_KM"
        ar_KW = "ar_KW"
        ar_LB = "ar_LB"
        ar_LY = "ar_LY"
        ar_MA = "ar_MA"
        ar_MR = "ar_MR"
        ar_OM = "ar_OM"
        ar_PS = "ar_PS"
        ar_QA = "ar_QA"
        ar_SA = "ar_SA"
        ar_SD = "ar_SD"
        ar_SO = "ar_SO"
        ar_SY = "ar_SY"
        ar_TD = "ar_TD"
        ar_TN = "ar_TN"
        ar_YE = "ar_YE"
        as_ = "as"
        as_IN = "as_IN"
        asa = "asa"
        asa_TZ = "asa_TZ"
        az = "az"
        az_Cyrl = "az_Cyrl"
        az_Cyrl_AZ = "az_Cyrl_AZ"
        az_Latn = "az_Latn"
        az_Latn_AZ = "az_Latn_AZ"
        bas = "bas"
        bas_CM = "bas_CM"
        be = "be"
        be_BY = "be_BY"
        bem = "bem"
        bem_ZM = "bem_ZM"
        bez = "bez"
        bez_TZ = "bez_TZ"
        bg = "bg"
        bg_BG = "bg_BG"
        bm = "bm"
        bm_ML = "bm_ML"
        bn = "bn"
        bn_BD = "bn_BD"
        bn_IN = "bn_IN"
        bo = "bo"
        bo_CN = "bo_CN"
        bo_IN = "bo_IN"
        br = "br"
        br_FR = "br_FR"
        brx = "brx"
        brx_IN = "brx_IN"
        bs = "bs"
        bs_Cyrl = "bs_Cyrl"
        bs_Cyrl_BA = "bs_Cyrl_BA"
        bs_Latn = "bs_Latn"
        bs_Latn_BA = "bs_Latn_BA"
        ca = "ca"
        ca_AD = "ca_AD"
        ca_ES = "ca_ES"
        cgg = "cgg"
        cgg_UG = "cgg_UG"
        chr = "chr"
        chr_US = "chr_US"
        cs = "cs"
        cs_CZ = "cs_CZ"
        cy = "cy"
        cy_GB = "cy_GB"
        da = "da"
        da_DK = "da_DK"
        dav = "dav"
        dav_KE = "dav_KE"
        de = "de"
        de_AT = "de_AT"
        de_BE = "de_BE"
        de_CH = "de_CH"
        de_DE = "de_DE"
        de_LI = "de_LI"
        de_LU = "de_LU"
        dje = "dje"
        dje_NE = "dje_NE"
        dua = "dua"
        dua_CM = "dua_CM"
        dyo = "dyo"
        dyo_SN = "dyo_SN"
        dz = "dz"
        dz_BT = "dz_BT"
        ebu = "ebu"
        ebu_KE = "ebu_KE"
        ee = "ee"
        ee_GH = "ee_GH"
        ee_TG = "ee_TG"
        el = "el"
        el_CY = "el_CY"
        el_GR = "el_GR"
        en = "en"
        en_150 = "en_150"
        en_AG = "en_AG"
        en_AS = "en_AS"
        en_AU = "en_AU"
        en_BB = "en_BB"
        en_BE = "en_BE"
        en_BM = "en_BM"
        en_BS = "en_BS"
        en_BW = "en_BW"
        en_BZ = "en_BZ"
        en_CA = "en_CA"
        en_CM = "en_CM"
        en_DM = "en_DM"
        en_FJ = "en_FJ"
        en_FM = "en_FM"
        en_GB = "en_GB"
        en_GD = "en_GD"
        en_GG = "en_GG"
        en_GH = "en_GH"
        en_GI = "en_GI"
        en_GM = "en_GM"
        en_GU = "en_GU"
        en_GY = "en_GY"
        en_HK = "en_HK"
        en_IE = "en_IE"
        en_IM = "en_IM"
        en_IN = "en_IN"
        en_JE = "en_JE"
        en_JM = "en_JM"
        en_KE = "en_KE"
        en_KI = "en_KI"
        en_KN = "en_KN"
        en_KY = "en_KY"
        en_LC = "en_LC"
        en_LR = "en_LR"
        en_LS = "en_LS"
        en_MG = "en_MG"
        en_MH = "en_MH"
        en_MP = "en_MP"
        en_MT = "en_MT"
        en_MU = "en_MU"
        en_MW = "en_MW"
        en_NA = "en_NA"
        en_NG = "en_NG"
        en_NZ = "en_NZ"
        en_PG = "en_PG"
        en_PH = "en_PH"
        en_PK = "en_PK"
        en_PR = "en_PR"
        en_PW = "en_PW"
        en_SB = "en_SB"
        en_SC = "en_SC"
        en_SG = "en_SG"
        en_SL = "en_SL"
        en_SS = "en_SS"
        en_SZ = "en_SZ"
        en_TC = "en_TC"
        en_TO = "en_TO"
        en_TT = "en_TT"
        en_TZ = "en_TZ"
        en_UG = "en_UG"
        en_UM = "en_UM"
        en_US = "en_US"
        en_US_POSIX = "en_US_POSIX"
        en_VC = "en_VC"
        en_VG = "en_VG"
        en_VI = "en_VI"
        en_VU = "en_VU"
        en_WS = "en_WS"
        en_ZA = "en_ZA"
        en_ZM = "en_ZM"
        en_ZW = "en_ZW"
        eo = "eo"
        es = "es"
        es_419 = "es_419"
        es_AR = "es_AR"
        es_BO = "es_BO"
        es_CL = "es_CL"
        es_CO = "es_CO"
        es_CR = "es_CR"
        es_CU = "es_CU"
        es_DO = "es_DO"
        es_EA = "es_EA"
        es_EC = "es_EC"
        es_ES = "es_ES"
        es_GQ = "es_GQ"
        es_GT = "es_GT"
        es_HN = "es_HN"
        es_IC = "es_IC"
        es_MX = "es_MX"
        es_NI = "es_NI"
        es_PA = "es_PA"
        es_PE = "es_PE"
        es_PH = "es_PH"
        es_PR = "es_PR"
        es_PY = "es_PY"
        es_SV = "es_SV"
        es_US = "es_US"
        es_UY = "es_UY"
        es_VE = "es_VE"
        et = "et"
        et_EE = "et_EE"
        eu = "eu"
        eu_ES = "eu_ES"
        ewo = "ewo"
        ewo_CM = "ewo_CM"
        fa = "fa"
        fa_AF = "fa_AF"
        fa_IR = "fa_IR"
        ff = "ff"
        ff_SN = "ff_SN"
        fi = "fi"
        fi_FI = "fi_FI"
        fil = "fil"
        fil_PH = "fil_PH"
        fo = "fo"
        fo_FO = "fo_FO"
        fr = "fr"
        fr_BE = "fr_BE"
        fr_BF = "fr_BF"
        fr_BI = "fr_BI"
        fr_BJ = "fr_BJ"
        fr_BL = "fr_BL"
        fr_CA = "fr_CA"
        fr_CD = "fr_CD"
        fr_CF = "fr_CF"
        fr_CG = "fr_CG"
        fr_CH = "fr_CH"
        fr_CI = "fr_CI"
        fr_CM = "fr_CM"
        fr_DJ = "fr_DJ"
        fr_DZ = "fr_DZ"
        fr_FR = "fr_FR"
        fr_GA = "fr_GA"
        fr_GF = "fr_GF"
        fr_GN = "fr_GN"
        fr_GP = "fr_GP"
        fr_GQ = "fr_GQ"
        fr_HT = "fr_HT"
        fr_KM = "fr_KM"
        fr_LU = "fr_LU"
        fr_MA = "fr_MA"
        fr_MC = "fr_MC"
        fr_MF = "fr_MF"
        fr_MG = "fr_MG"
        fr_ML = "fr_ML"
        fr_MQ = "fr_MQ"
        fr_MR = "fr_MR"
        fr_MU = "fr_MU"
        fr_NC = "fr_NC"
        fr_NE = "fr_NE"
        fr_PF = "fr_PF"
        fr_RE = "fr_RE"
        fr_RW = "fr_RW"
        fr_SC = "fr_SC"
        fr_SN = "fr_SN"
        fr_SY = "fr_SY"
        fr_TD = "fr_TD"
        fr_TG = "fr_TG"
        fr_TN = "fr_TN"
        fr_VU = "fr_VU"
        fr_YT = "fr_YT"
        ga = "ga"
        ga_IE = "ga_IE"
        gl = "gl"
        gl_ES = "gl_ES"
        gsw = "gsw"
        gsw_CH = "gsw_CH"
        gu = "gu"
        gu_IN = "gu_IN"
        guz = "guz"
        guz_KE = "guz_KE"
        gv = "gv"
        gv_GB = "gv_GB"
        ha = "ha"
        ha_Latn = "ha_Latn"
        ha_Latn_GH = "ha_Latn_GH"
        ha_Latn_NE = "ha_Latn_NE"
        ha_Latn_NG = "ha_Latn_NG"
        haw = "haw"
        haw_US = "haw_US"
        he = "he"
        he_IL = "he_IL"
        hi = "hi"
        hi_IN = "hi_IN"
        hr = "hr"
        hr_BA = "hr_BA"
        hr_HR = "hr_HR"
        hu = "hu"
        hu_HU = "hu_HU"
        hy = "hy"
        hy_AM = "hy_AM"
        id = "id"
        id_ID = "id_ID"
        ig = "ig"
        ig_NG = "ig_NG"
        ii = "ii"
        ii_CN = "ii_CN"
        is_ = "is"
        is_IS = "is_IS"
        it = "it"
        it_CH = "it_CH"
        it_IT = "it_IT"
        it_SM = "it_SM"
        ja = "ja"
        ja_JP = "ja_JP"
        jgo = "jgo"
        jgo_CM = "jgo_CM"
        jmc = "jmc"
        jmc_TZ = "jmc_TZ"
        ka = "ka"
        ka_GE = "ka_GE"
        kab = "kab"
        kab_DZ = "kab_DZ"
        kam = "kam"
        kam_KE = "kam_KE"
        kde = "kde"
        kde_TZ = "kde_TZ"
        kea = "kea"
        kea_CV = "kea_CV"
        khq = "khq"
        khq_ML = "khq_ML"
        ki = "ki"
        ki_KE = "ki_KE"
        kk = "kk"
        kk_Cyrl = "kk_Cyrl"
        kk_Cyrl_KZ = "kk_Cyrl_KZ"
        kl = "kl"
        kl_GL = "kl_GL"
        kln = "kln"
        kln_KE = "kln_KE"
        km = "km"
        km_KH = "km_KH"
        kn = "kn"
        kn_IN = "kn_IN"
        ko = "ko"
        ko_KP = "ko_KP"
        ko_KR = "ko_KR"
        kok = "kok"
        kok_IN = "kok_IN"
        ks = "ks"
        ks_Arab = "ks_Arab"
        ks_Arab_IN = "ks_Arab_IN"
        ksb = "ksb"
        ksb_TZ = "ksb_TZ"
        ksf = "ksf"
        ksf_CM = "ksf_CM"
        kw = "kw"
        kw_GB = "kw_GB"
        lag = "lag"
        lag_TZ = "lag_TZ"
        lg = "lg"
        lg_UG = "lg_UG"
        ln = "ln"
        ln_AO = "ln_AO"
        ln_CD = "ln_CD"
        ln_CF = "ln_CF"
        ln_CG = "ln_CG"
        lo = "lo"
        lo_LA = "lo_LA"
        lt = "lt"
        lt_LT = "lt_LT"
        lu = "lu"
        lu_CD = "lu_CD"
        luo = "luo"
        luo_KE = "luo_KE"
        luy = "luy"
        luy_KE = "luy_KE"
        lv = "lv"
        lv_LV = "lv_LV"
        mas = "mas"
        mas_KE = "mas_KE"
        mas_TZ = "mas_TZ"
        mer = "mer"
        mer_KE = "mer_KE"
        mfe = "mfe"
        mfe_MU = "mfe_MU"
        mg = "mg"
        mg_MG = "mg_MG"
        mgh = "mgh"
        mgh_MZ = "mgh_MZ"
        mgo = "mgo"
        mgo_CM = "mgo_CM"
        mk = "mk"
        mk_MK = "mk_MK"
        ml = "ml"
        ml_IN = "ml_IN"
        mr = "mr"
        mr_IN = "mr_IN"
        ms = "ms"
        ms_BN = "ms_BN"
        ms_MY = "ms_MY"
        ms_SG = "ms_SG"
        mt = "mt"
        mt_MT = "mt_MT"
        mua = "mua"
        mua_CM = "mua_CM"
        my = "my"
        my_MM = "my_MM"
        naq = "naq"
        naq_NA = "naq_NA"
        nb = "nb"
        nb_NO = "nb_NO"
        nd = "nd"
        nd_ZW = "nd_ZW"
        ne = "ne"
        ne_IN = "ne_IN"
        ne_NP = "ne_NP"
        nl = "nl"
        nl_AW = "nl_AW"
        nl_BE = "nl_BE"
        nl_CW = "nl_CW"
        nl_NL = "nl_NL"
        nl_SR = "nl_SR"
        nl_SX = "nl_SX"
        nmg = "nmg"
        nmg_CM = "nmg_CM"
        nn = "nn"
        nn_NO = "nn_NO"
        nus = "nus"
        nus_SD = "nus_SD"
        nyn = "nyn"
        nyn_UG = "nyn_UG"
        om = "om"
        om_ET = "om_ET"
        om_KE = "om_KE"
        or_ = "or"
        or_IN = "or_IN"
        pa = "pa"
        pa_Arab = "pa_Arab"
        pa_Arab_PK = "pa_Arab_PK"
        pa_Guru = "pa_Guru"
        pa_Guru_IN = "pa_Guru_IN"
        pl = "pl"
        pl_PL = "pl_PL"
        ps = "ps"
        ps_AF = "ps_AF"
        pt = "pt"
        pt_AO = "pt_AO"
        pt_BR = "pt_BR"
        pt_CV = "pt_CV"
        pt_GW = "pt_GW"
        pt_MO = "pt_MO"
        pt_MZ = "pt_MZ"
        pt_PT = "pt_PT"
        pt_ST = "pt_ST"
        pt_TL = "pt_TL"
        rm = "rm"
        rm_CH = "rm_CH"
        rn = "rn"
        rn_BI = "rn_BI"
        ro = "ro"
        ro_MD = "ro_MD"
        ro_RO = "ro_RO"
        rof = "rof"
        rof_TZ = "rof_TZ"
        ru = "ru"
        ru_BY = "ru_BY"
        ru_KG = "ru_KG"
        ru_KZ = "ru_KZ"
        ru_MD = "ru_MD"
        ru_RU = "ru_RU"
        ru_UA = "ru_UA"
        rw = "rw"
        rw_RW = "rw_RW"
        rwk = "rwk"
        rwk_TZ = "rwk_TZ"
        saq = "saq"
        saq_KE = "saq_KE"
        sbp = "sbp"
        sbp_TZ = "sbp_TZ"
        seh = "seh"
        seh_MZ = "seh_MZ"
        ses = "ses"
        ses_ML = "ses_ML"
        sg = "sg"
        sg_CF = "sg_CF"
        shi = "shi"
        shi_Latn = "shi_Latn"
        shi_Latn_MA = "shi_Latn_MA"
        shi_Tfng = "shi_Tfng"
        shi_Tfng_MA = "shi_Tfng_MA"
        si = "si"
        si_LK = "si_LK"
        sk = "sk"
        sk_SK = "sk_SK"
        sl = "sl"
        sl_SI = "sl_SI"
        sn = "sn"
        sn_ZW = "sn_ZW"
        so = "so"
        so_DJ = "so_DJ"
        so_ET = "so_ET"
        so_KE = "so_KE"
        so_SO = "so_SO"
        sq = "sq"
        sq_AL = "sq_AL"
        sq_MK = "sq_MK"
        sr = "sr"
        sr_Cyrl = "sr_Cyrl"
        sr_Cyrl_BA = "sr_Cyrl_BA"
        sr_Cyrl_ME = "sr_Cyrl_ME"
        sr_Cyrl_RS = "sr_Cyrl_RS"
        sr_Latn = "sr_Latn"
        sr_Latn_BA = "sr_Latn_BA"
        sr_Latn_ME = "sr_Latn_ME"
        sr_Latn_RS = "sr_Latn_RS"
        sv = "sv"
        sv_AX = "sv_AX"
        sv_FI = "sv_FI"
        sv_SE = "sv_SE"
        sw = "sw"
        sw_KE = "sw_KE"
        sw_TZ = "sw_TZ"
        sw_UG = "sw_UG"
        swc = "swc"
        swc_CD = "swc_CD"
        ta = "ta"
        ta_IN = "ta_IN"
        ta_LK = "ta_LK"
        ta_MY = "ta_MY"
        ta_SG = "ta_SG"
        te = "te"
        te_IN = "te_IN"
        teo = "teo"
        teo_KE = "teo_KE"
        teo_UG = "teo_UG"
        th = "th"
        th_TH = "th_TH"
        ti = "ti"
        ti_ER = "ti_ER"
        ti_ET = "ti_ET"
        to = "to"
        to_TO = "to_TO"
        tr = "tr"
        tr_CY = "tr_CY"
        tr_TR = "tr_TR"
        twq = "twq"
        twq_NE = "twq_NE"
        tzm = "tzm"
        tzm_Latn = "tzm_Latn"
        tzm_Latn_MA = "tzm_Latn_MA"
        uk = "uk"
        uk_UA = "uk_UA"
        ur = "ur"
        ur_IN = "ur_IN"
        ur_PK = "ur_PK"
        uz = "uz"
        uz_Arab = "uz_Arab"
        uz_Arab_AF = "uz_Arab_AF"
        uz_Cyrl = "uz_Cyrl"
        uz_Cyrl_UZ = "uz_Cyrl_UZ"
        uz_Latn = "uz_Latn"
        uz_Latn_UZ = "uz_Latn_UZ"
        vai = "vai"
        vai_Latn = "vai_Latn"
        vai_Latn_LR = "vai_Latn_LR"
        vai_Vaii = "vai_Vaii"
        vai_Vaii_LR = "vai_Vaii_LR"
        vi = "vi"
        vi_VN = "vi_VN"
        vun = "vun"
        vun_TZ = "vun_TZ"
        xog = "xog"
        xog_UG = "xog_UG"
        yav = "yav"
        yav_CM = "yav_CM"
        yo = "yo"
        yo_NG = "yo_NG"
        zh = "zh"
        zh_Hans = "zh_Hans"
        zh_Hans_CN = "zh_Hans_CN"
        zh_Hans_HK = "zh_Hans_HK"
        zh_Hans_MO = "zh_Hans_MO"
        zh_Hans_SG = "zh_Hans_SG"
        zh_Hant = "zh_Hant"
        zh_Hant_HK = "zh_Hant_HK"
        zh_Hant_MO = "zh_Hant_MO"
        zh_Hant_TW = "zh_Hant_TW"
        zu = "zu"
        zu_ZA = "zu_ZA"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class CHANGE_APPLY:
    """Enums for properties in the CHANGE_APPLY stage."""

    class Selection(Enum):
        """Enum for the Selection property."""

        allkeys = "allkeys"
        custom = " "
        allvalues = "allvalues"

    class SelectionCiCs(Enum):
        """Enum for the SelectionCiCs property."""

        cs = "cs"
        ci = "ci"

    class SelectionAscDesc(Enum):
        """Enum for the SelectionAscDesc property."""

        desc = "desc"
        asc = "asc"

    class SelectionNulls(Enum):
        """Enum for the SelectionNulls property."""

        last = "last"
        first = "first"

    class DoStats(Enum):
        """Enum for the DoStats property."""

        true = "doStats"
        false = " "

    class IgnoreDeleteValues(Enum):
        """Enum for the IgnoreDeleteValues property."""

        false = " "
        true = "ignoreDeleteValues"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_set = -2
        clear = 0
        set = 1

    class CollationSequence(Enum):
        """Enum for the CollationSequence property."""

        OFF = "OFF"
        af = "af"
        af_NA = "af_NA"
        af_ZA = "af_ZA"
        agq = "agq"
        agq_CM = "agq_CM"
        ak = "ak"
        ak_GH = "ak_GH"
        am = "am"
        am_ET = "am_ET"
        ar = "ar"
        ar_001 = "ar_001"
        ar_AE = "ar_AE"
        ar_BH = "ar_BH"
        ar_DJ = "ar_DJ"
        ar_DZ = "ar_DZ"
        ar_EG = "ar_EG"
        ar_EH = "ar_EH"
        ar_ER = "ar_ER"
        ar_IL = "ar_IL"
        ar_IQ = "ar_IQ"
        ar_JO = "ar_JO"
        ar_KM = "ar_KM"
        ar_KW = "ar_KW"
        ar_LB = "ar_LB"
        ar_LY = "ar_LY"
        ar_MA = "ar_MA"
        ar_MR = "ar_MR"
        ar_OM = "ar_OM"
        ar_PS = "ar_PS"
        ar_QA = "ar_QA"
        ar_SA = "ar_SA"
        ar_SD = "ar_SD"
        ar_SO = "ar_SO"
        ar_SY = "ar_SY"
        ar_TD = "ar_TD"
        ar_TN = "ar_TN"
        ar_YE = "ar_YE"
        as_ = "as"
        as_IN = "as_IN"
        asa = "asa"
        asa_TZ = "asa_TZ"
        az = "az"
        az_Cyrl = "az_Cyrl"
        az_Cyrl_AZ = "az_Cyrl_AZ"
        az_Latn = "az_Latn"
        az_Latn_AZ = "az_Latn_AZ"
        bas = "bas"
        bas_CM = "bas_CM"
        be = "be"
        be_BY = "be_BY"
        bem = "bem"
        bem_ZM = "bem_ZM"
        bez = "bez"
        bez_TZ = "bez_TZ"
        bg = "bg"
        bg_BG = "bg_BG"
        bm = "bm"
        bm_ML = "bm_ML"
        bn = "bn"
        bn_BD = "bn_BD"
        bn_IN = "bn_IN"
        bo = "bo"
        bo_CN = "bo_CN"
        bo_IN = "bo_IN"
        br = "br"
        br_FR = "br_FR"
        brx = "brx"
        brx_IN = "brx_IN"
        bs = "bs"
        bs_Cyrl = "bs_Cyrl"
        bs_Cyrl_BA = "bs_Cyrl_BA"
        bs_Latn = "bs_Latn"
        bs_Latn_BA = "bs_Latn_BA"
        ca = "ca"
        ca_AD = "ca_AD"
        ca_ES = "ca_ES"
        cgg = "cgg"
        cgg_UG = "cgg_UG"
        chr = "chr"
        chr_US = "chr_US"
        cs = "cs"
        cs_CZ = "cs_CZ"
        cy = "cy"
        cy_GB = "cy_GB"
        da = "da"
        da_DK = "da_DK"
        dav = "dav"
        dav_KE = "dav_KE"
        de = "de"
        de_AT = "de_AT"
        de_BE = "de_BE"
        de_CH = "de_CH"
        de_DE = "de_DE"
        de_LI = "de_LI"
        de_LU = "de_LU"
        dje = "dje"
        dje_NE = "dje_NE"
        dua = "dua"
        dua_CM = "dua_CM"
        dyo = "dyo"
        dyo_SN = "dyo_SN"
        dz = "dz"
        dz_BT = "dz_BT"
        ebu = "ebu"
        ebu_KE = "ebu_KE"
        ee = "ee"
        ee_GH = "ee_GH"
        ee_TG = "ee_TG"
        el = "el"
        el_CY = "el_CY"
        el_GR = "el_GR"
        en = "en"
        en_150 = "en_150"
        en_AG = "en_AG"
        en_AS = "en_AS"
        en_AU = "en_AU"
        en_BB = "en_BB"
        en_BE = "en_BE"
        en_BM = "en_BM"
        en_BS = "en_BS"
        en_BW = "en_BW"
        en_BZ = "en_BZ"
        en_CA = "en_CA"
        en_CM = "en_CM"
        en_DM = "en_DM"
        en_FJ = "en_FJ"
        en_FM = "en_FM"
        en_GB = "en_GB"
        en_GD = "en_GD"
        en_GG = "en_GG"
        en_GH = "en_GH"
        en_GI = "en_GI"
        en_GM = "en_GM"
        en_GU = "en_GU"
        en_GY = "en_GY"
        en_HK = "en_HK"
        en_IE = "en_IE"
        en_IM = "en_IM"
        en_IN = "en_IN"
        en_JE = "en_JE"
        en_JM = "en_JM"
        en_KE = "en_KE"
        en_KI = "en_KI"
        en_KN = "en_KN"
        en_KY = "en_KY"
        en_LC = "en_LC"
        en_LR = "en_LR"
        en_LS = "en_LS"
        en_MG = "en_MG"
        en_MH = "en_MH"
        en_MP = "en_MP"
        en_MT = "en_MT"
        en_MU = "en_MU"
        en_MW = "en_MW"
        en_NA = "en_NA"
        en_NG = "en_NG"
        en_NZ = "en_NZ"
        en_PG = "en_PG"
        en_PH = "en_PH"
        en_PK = "en_PK"
        en_PR = "en_PR"
        en_PW = "en_PW"
        en_SB = "en_SB"
        en_SC = "en_SC"
        en_SG = "en_SG"
        en_SL = "en_SL"
        en_SS = "en_SS"
        en_SZ = "en_SZ"
        en_TC = "en_TC"
        en_TO = "en_TO"
        en_TT = "en_TT"
        en_TZ = "en_TZ"
        en_UG = "en_UG"
        en_UM = "en_UM"
        en_US = "en_US"
        en_US_POSIX = "en_US_POSIX"
        en_VC = "en_VC"
        en_VG = "en_VG"
        en_VI = "en_VI"
        en_VU = "en_VU"
        en_WS = "en_WS"
        en_ZA = "en_ZA"
        en_ZM = "en_ZM"
        en_ZW = "en_ZW"
        eo = "eo"
        es = "es"
        es_419 = "es_419"
        es_AR = "es_AR"
        es_BO = "es_BO"
        es_CL = "es_CL"
        es_CO = "es_CO"
        es_CR = "es_CR"
        es_CU = "es_CU"
        es_DO = "es_DO"
        es_EA = "es_EA"
        es_EC = "es_EC"
        es_ES = "es_ES"
        es_GQ = "es_GQ"
        es_GT = "es_GT"
        es_HN = "es_HN"
        es_IC = "es_IC"
        es_MX = "es_MX"
        es_NI = "es_NI"
        es_PA = "es_PA"
        es_PE = "es_PE"
        es_PH = "es_PH"
        es_PR = "es_PR"
        es_PY = "es_PY"
        es_SV = "es_SV"
        es_US = "es_US"
        es_UY = "es_UY"
        es_VE = "es_VE"
        et = "et"
        et_EE = "et_EE"
        eu = "eu"
        eu_ES = "eu_ES"
        ewo = "ewo"
        ewo_CM = "ewo_CM"
        fa = "fa"
        fa_AF = "fa_AF"
        fa_IR = "fa_IR"
        ff = "ff"
        ff_SN = "ff_SN"
        fi = "fi"
        fi_FI = "fi_FI"
        fil = "fil"
        fil_PH = "fil_PH"
        fo = "fo"
        fo_FO = "fo_FO"
        fr = "fr"
        fr_BE = "fr_BE"
        fr_BF = "fr_BF"
        fr_BI = "fr_BI"
        fr_BJ = "fr_BJ"
        fr_BL = "fr_BL"
        fr_CA = "fr_CA"
        fr_CD = "fr_CD"
        fr_CF = "fr_CF"
        fr_CG = "fr_CG"
        fr_CH = "fr_CH"
        fr_CI = "fr_CI"
        fr_CM = "fr_CM"
        fr_DJ = "fr_DJ"
        fr_DZ = "fr_DZ"
        fr_FR = "fr_FR"
        fr_GA = "fr_GA"
        fr_GF = "fr_GF"
        fr_GN = "fr_GN"
        fr_GP = "fr_GP"
        fr_GQ = "fr_GQ"
        fr_HT = "fr_HT"
        fr_KM = "fr_KM"
        fr_LU = "fr_LU"
        fr_MA = "fr_MA"
        fr_MC = "fr_MC"
        fr_MF = "fr_MF"
        fr_MG = "fr_MG"
        fr_ML = "fr_ML"
        fr_MQ = "fr_MQ"
        fr_MR = "fr_MR"
        fr_MU = "fr_MU"
        fr_NC = "fr_NC"
        fr_NE = "fr_NE"
        fr_PF = "fr_PF"
        fr_RE = "fr_RE"
        fr_RW = "fr_RW"
        fr_SC = "fr_SC"
        fr_SN = "fr_SN"
        fr_SY = "fr_SY"
        fr_TD = "fr_TD"
        fr_TG = "fr_TG"
        fr_TN = "fr_TN"
        fr_VU = "fr_VU"
        fr_YT = "fr_YT"
        ga = "ga"
        ga_IE = "ga_IE"
        gl = "gl"
        gl_ES = "gl_ES"
        gsw = "gsw"
        gsw_CH = "gsw_CH"
        gu = "gu"
        gu_IN = "gu_IN"
        guz = "guz"
        guz_KE = "guz_KE"
        gv = "gv"
        gv_GB = "gv_GB"
        ha = "ha"
        ha_Latn = "ha_Latn"
        ha_Latn_GH = "ha_Latn_GH"
        ha_Latn_NE = "ha_Latn_NE"
        ha_Latn_NG = "ha_Latn_NG"
        haw = "haw"
        haw_US = "haw_US"
        he = "he"
        he_IL = "he_IL"
        hi = "hi"
        hi_IN = "hi_IN"
        hr = "hr"
        hr_BA = "hr_BA"
        hr_HR = "hr_HR"
        hu = "hu"
        hu_HU = "hu_HU"
        hy = "hy"
        hy_AM = "hy_AM"
        id = "id"
        id_ID = "id_ID"
        ig = "ig"
        ig_NG = "ig_NG"
        ii = "ii"
        ii_CN = "ii_CN"
        is_ = "is"
        is_IS = "is_IS"
        it = "it"
        it_CH = "it_CH"
        it_IT = "it_IT"
        it_SM = "it_SM"
        ja = "ja"
        ja_JP = "ja_JP"
        jgo = "jgo"
        jgo_CM = "jgo_CM"
        jmc = "jmc"
        jmc_TZ = "jmc_TZ"
        ka = "ka"
        ka_GE = "ka_GE"
        kab = "kab"
        kab_DZ = "kab_DZ"
        kam = "kam"
        kam_KE = "kam_KE"
        kde = "kde"
        kde_TZ = "kde_TZ"
        kea = "kea"
        kea_CV = "kea_CV"
        khq = "khq"
        khq_ML = "khq_ML"
        ki = "ki"
        ki_KE = "ki_KE"
        kk = "kk"
        kk_Cyrl = "kk_Cyrl"
        kk_Cyrl_KZ = "kk_Cyrl_KZ"
        kl = "kl"
        kl_GL = "kl_GL"
        kln = "kln"
        kln_KE = "kln_KE"
        km = "km"
        km_KH = "km_KH"
        kn = "kn"
        kn_IN = "kn_IN"
        ko = "ko"
        ko_KP = "ko_KP"
        ko_KR = "ko_KR"
        kok = "kok"
        kok_IN = "kok_IN"
        ks = "ks"
        ks_Arab = "ks_Arab"
        ks_Arab_IN = "ks_Arab_IN"
        ksb = "ksb"
        ksb_TZ = "ksb_TZ"
        ksf = "ksf"
        ksf_CM = "ksf_CM"
        kw = "kw"
        kw_GB = "kw_GB"
        lag = "lag"
        lag_TZ = "lag_TZ"
        lg = "lg"
        lg_UG = "lg_UG"
        ln = "ln"
        ln_AO = "ln_AO"
        ln_CD = "ln_CD"
        ln_CF = "ln_CF"
        ln_CG = "ln_CG"
        lo = "lo"
        lo_LA = "lo_LA"
        lt = "lt"
        lt_LT = "lt_LT"
        lu = "lu"
        lu_CD = "lu_CD"
        luo = "luo"
        luo_KE = "luo_KE"
        luy = "luy"
        luy_KE = "luy_KE"
        lv = "lv"
        lv_LV = "lv_LV"
        mas = "mas"
        mas_KE = "mas_KE"
        mas_TZ = "mas_TZ"
        mer = "mer"
        mer_KE = "mer_KE"
        mfe = "mfe"
        mfe_MU = "mfe_MU"
        mg = "mg"
        mg_MG = "mg_MG"
        mgh = "mgh"
        mgh_MZ = "mgh_MZ"
        mgo = "mgo"
        mgo_CM = "mgo_CM"
        mk = "mk"
        mk_MK = "mk_MK"
        ml = "ml"
        ml_IN = "ml_IN"
        mr = "mr"
        mr_IN = "mr_IN"
        ms = "ms"
        ms_BN = "ms_BN"
        ms_MY = "ms_MY"
        ms_SG = "ms_SG"
        mt = "mt"
        mt_MT = "mt_MT"
        mua = "mua"
        mua_CM = "mua_CM"
        my = "my"
        my_MM = "my_MM"
        naq = "naq"
        naq_NA = "naq_NA"
        nb = "nb"
        nb_NO = "nb_NO"
        nd = "nd"
        nd_ZW = "nd_ZW"
        ne = "ne"
        ne_IN = "ne_IN"
        ne_NP = "ne_NP"
        nl = "nl"
        nl_AW = "nl_AW"
        nl_BE = "nl_BE"
        nl_CW = "nl_CW"
        nl_NL = "nl_NL"
        nl_SR = "nl_SR"
        nl_SX = "nl_SX"
        nmg = "nmg"
        nmg_CM = "nmg_CM"
        nn = "nn"
        nn_NO = "nn_NO"
        nus = "nus"
        nus_SD = "nus_SD"
        nyn = "nyn"
        nyn_UG = "nyn_UG"
        om = "om"
        om_ET = "om_ET"
        om_KE = "om_KE"
        or_ = "or"
        or_IN = "or_IN"
        pa = "pa"
        pa_Arab = "pa_Arab"
        pa_Arab_PK = "pa_Arab_PK"
        pa_Guru = "pa_Guru"
        pa_Guru_IN = "pa_Guru_IN"
        pl = "pl"
        pl_PL = "pl_PL"
        ps = "ps"
        ps_AF = "ps_AF"
        pt = "pt"
        pt_AO = "pt_AO"
        pt_BR = "pt_BR"
        pt_CV = "pt_CV"
        pt_GW = "pt_GW"
        pt_MO = "pt_MO"
        pt_MZ = "pt_MZ"
        pt_PT = "pt_PT"
        pt_ST = "pt_ST"
        pt_TL = "pt_TL"
        rm = "rm"
        rm_CH = "rm_CH"
        rn = "rn"
        rn_BI = "rn_BI"
        ro = "ro"
        ro_MD = "ro_MD"
        ro_RO = "ro_RO"
        rof = "rof"
        rof_TZ = "rof_TZ"
        ru = "ru"
        ru_BY = "ru_BY"
        ru_KG = "ru_KG"
        ru_KZ = "ru_KZ"
        ru_MD = "ru_MD"
        ru_RU = "ru_RU"
        ru_UA = "ru_UA"
        rw = "rw"
        rw_RW = "rw_RW"
        rwk = "rwk"
        rwk_TZ = "rwk_TZ"
        saq = "saq"
        saq_KE = "saq_KE"
        sbp = "sbp"
        sbp_TZ = "sbp_TZ"
        seh = "seh"
        seh_MZ = "seh_MZ"
        ses = "ses"
        ses_ML = "ses_ML"
        sg = "sg"
        sg_CF = "sg_CF"
        shi = "shi"
        shi_Latn = "shi_Latn"
        shi_Latn_MA = "shi_Latn_MA"
        shi_Tfng = "shi_Tfng"
        shi_Tfng_MA = "shi_Tfng_MA"
        si = "si"
        si_LK = "si_LK"
        sk = "sk"
        sk_SK = "sk_SK"
        sl = "sl"
        sl_SI = "sl_SI"
        sn = "sn"
        sn_ZW = "sn_ZW"
        so = "so"
        so_DJ = "so_DJ"
        so_ET = "so_ET"
        so_KE = "so_KE"
        so_SO = "so_SO"
        sq = "sq"
        sq_AL = "sq_AL"
        sq_MK = "sq_MK"
        sr = "sr"
        sr_Cyrl = "sr_Cyrl"
        sr_Cyrl_BA = "sr_Cyrl_BA"
        sr_Cyrl_ME = "sr_Cyrl_ME"
        sr_Cyrl_RS = "sr_Cyrl_RS"
        sr_Latn = "sr_Latn"
        sr_Latn_BA = "sr_Latn_BA"
        sr_Latn_ME = "sr_Latn_ME"
        sr_Latn_RS = "sr_Latn_RS"
        sv = "sv"
        sv_AX = "sv_AX"
        sv_FI = "sv_FI"
        sv_SE = "sv_SE"
        sw = "sw"
        sw_KE = "sw_KE"
        sw_TZ = "sw_TZ"
        sw_UG = "sw_UG"
        swc = "swc"
        swc_CD = "swc_CD"
        ta = "ta"
        ta_IN = "ta_IN"
        ta_LK = "ta_LK"
        ta_MY = "ta_MY"
        ta_SG = "ta_SG"
        te = "te"
        te_IN = "te_IN"
        teo = "teo"
        teo_KE = "teo_KE"
        teo_UG = "teo_UG"
        th = "th"
        th_TH = "th_TH"
        ti = "ti"
        ti_ER = "ti_ER"
        ti_ET = "ti_ET"
        to = "to"
        to_TO = "to_TO"
        tr = "tr"
        tr_CY = "tr_CY"
        tr_TR = "tr_TR"
        twq = "twq"
        twq_NE = "twq_NE"
        tzm = "tzm"
        tzm_Latn = "tzm_Latn"
        tzm_Latn_MA = "tzm_Latn_MA"
        uk = "uk"
        uk_UA = "uk_UA"
        ur = "ur"
        ur_IN = "ur_IN"
        ur_PK = "ur_PK"
        uz = "uz"
        uz_Arab = "uz_Arab"
        uz_Arab_AF = "uz_Arab_AF"
        uz_Cyrl = "uz_Cyrl"
        uz_Cyrl_UZ = "uz_Cyrl_UZ"
        uz_Latn = "uz_Latn"
        uz_Latn_UZ = "uz_Latn_UZ"
        vai = "vai"
        vai_Latn = "vai_Latn"
        vai_Latn_LR = "vai_Latn_LR"
        vai_Vaii = "vai_Vaii"
        vai_Vaii_LR = "vai_Vaii_LR"
        vi = "vi"
        vi_VN = "vi_VN"
        vun = "vun"
        vun_TZ = "vun_TZ"
        xog = "xog"
        xog_UG = "xog_UG"
        yav = "yav"
        yav_CM = "yav_CM"
        yo = "yo"
        yo_NG = "yo_NG"
        zh = "zh"
        zh_Hans = "zh_Hans"
        zh_Hans_CN = "zh_Hans_CN"
        zh_Hans_HK = "zh_Hans_HK"
        zh_Hans_MO = "zh_Hans_MO"
        zh_Hans_SG = "zh_Hans_SG"
        zh_Hant = "zh_Hant"
        zh_Hant_HK = "zh_Hant_HK"
        zh_Hant_MO = "zh_Hant_MO"
        zh_Hant_TW = "zh_Hant_TW"
        zu = "zu"
        zu_ZA = "zu_ZA"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class PIVOT:
    """Enums for properties in the PIVOT stage."""

    class PivotType(Enum):
        """Enum for the PivotType property."""

        verticalpivot = "verticalpivot"
        pivot = "pivot"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class CHECKSUM:
    """Enums for properties in the CHECKSUM stage."""

    class CompMode(Enum):
        """Enum for the CompMode property."""

        all = " "
        keepcol = "keepcol"
        dropcol = "dropcol"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class WRITE_RANGE_MAP:
    """Enums for properties in the WRITE_RANGE_MAP stage."""

    class Overwrite(Enum):
        """Enum for the Overwrite property."""

        true = "overwrite"
        false = " "

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_seq = "default_seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class DATA_RULES:
    """Enums for properties in the DATA_RULES stage."""

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class COMBINE_RECORDS:
    """Enums for properties in the COMBINE_RECORDS stage."""

    class Toplevelkeys(Enum):
        """Enum for the Toplevelkeys property."""

        true = "toplevelkeys"
        false = " "

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class CollationSequence(Enum):
        """Enum for the CollationSequence property."""

        OFF = "OFF"
        af = "af"
        af_NA = "af_NA"
        af_ZA = "af_ZA"
        agq = "agq"
        agq_CM = "agq_CM"
        ak = "ak"
        ak_GH = "ak_GH"
        am = "am"
        am_ET = "am_ET"
        ar = "ar"
        ar_001 = "ar_001"
        ar_AE = "ar_AE"
        ar_BH = "ar_BH"
        ar_DJ = "ar_DJ"
        ar_DZ = "ar_DZ"
        ar_EG = "ar_EG"
        ar_EH = "ar_EH"
        ar_ER = "ar_ER"
        ar_IL = "ar_IL"
        ar_IQ = "ar_IQ"
        ar_JO = "ar_JO"
        ar_KM = "ar_KM"
        ar_KW = "ar_KW"
        ar_LB = "ar_LB"
        ar_LY = "ar_LY"
        ar_MA = "ar_MA"
        ar_MR = "ar_MR"
        ar_OM = "ar_OM"
        ar_PS = "ar_PS"
        ar_QA = "ar_QA"
        ar_SA = "ar_SA"
        ar_SD = "ar_SD"
        ar_SO = "ar_SO"
        ar_SY = "ar_SY"
        ar_TD = "ar_TD"
        ar_TN = "ar_TN"
        ar_YE = "ar_YE"
        as_ = "as"
        as_IN = "as_IN"
        asa = "asa"
        asa_TZ = "asa_TZ"
        az = "az"
        az_Cyrl = "az_Cyrl"
        az_Cyrl_AZ = "az_Cyrl_AZ"
        az_Latn = "az_Latn"
        az_Latn_AZ = "az_Latn_AZ"
        bas = "bas"
        bas_CM = "bas_CM"
        be = "be"
        be_BY = "be_BY"
        bem = "bem"
        bem_ZM = "bem_ZM"
        bez = "bez"
        bez_TZ = "bez_TZ"
        bg = "bg"
        bg_BG = "bg_BG"
        bm = "bm"
        bm_ML = "bm_ML"
        bn = "bn"
        bn_BD = "bn_BD"
        bn_IN = "bn_IN"
        bo = "bo"
        bo_CN = "bo_CN"
        bo_IN = "bo_IN"
        br = "br"
        br_FR = "br_FR"
        brx = "brx"
        brx_IN = "brx_IN"
        bs = "bs"
        bs_Cyrl = "bs_Cyrl"
        bs_Cyrl_BA = "bs_Cyrl_BA"
        bs_Latn = "bs_Latn"
        bs_Latn_BA = "bs_Latn_BA"
        ca = "ca"
        ca_AD = "ca_AD"
        ca_ES = "ca_ES"
        cgg = "cgg"
        cgg_UG = "cgg_UG"
        chr = "chr"
        chr_US = "chr_US"
        cs = "cs"
        cs_CZ = "cs_CZ"
        cy = "cy"
        cy_GB = "cy_GB"
        da = "da"
        da_DK = "da_DK"
        dav = "dav"
        dav_KE = "dav_KE"
        de = "de"
        de_AT = "de_AT"
        de_BE = "de_BE"
        de_CH = "de_CH"
        de_DE = "de_DE"
        de_LI = "de_LI"
        de_LU = "de_LU"
        dje = "dje"
        dje_NE = "dje_NE"
        dua = "dua"
        dua_CM = "dua_CM"
        dyo = "dyo"
        dyo_SN = "dyo_SN"
        dz = "dz"
        dz_BT = "dz_BT"
        ebu = "ebu"
        ebu_KE = "ebu_KE"
        ee = "ee"
        ee_GH = "ee_GH"
        ee_TG = "ee_TG"
        el = "el"
        el_CY = "el_CY"
        el_GR = "el_GR"
        en = "en"
        en_150 = "en_150"
        en_AG = "en_AG"
        en_AS = "en_AS"
        en_AU = "en_AU"
        en_BB = "en_BB"
        en_BE = "en_BE"
        en_BM = "en_BM"
        en_BS = "en_BS"
        en_BW = "en_BW"
        en_BZ = "en_BZ"
        en_CA = "en_CA"
        en_CM = "en_CM"
        en_DM = "en_DM"
        en_FJ = "en_FJ"
        en_FM = "en_FM"
        en_GB = "en_GB"
        en_GD = "en_GD"
        en_GG = "en_GG"
        en_GH = "en_GH"
        en_GI = "en_GI"
        en_GM = "en_GM"
        en_GU = "en_GU"
        en_GY = "en_GY"
        en_HK = "en_HK"
        en_IE = "en_IE"
        en_IM = "en_IM"
        en_IN = "en_IN"
        en_JE = "en_JE"
        en_JM = "en_JM"
        en_KE = "en_KE"
        en_KI = "en_KI"
        en_KN = "en_KN"
        en_KY = "en_KY"
        en_LC = "en_LC"
        en_LR = "en_LR"
        en_LS = "en_LS"
        en_MG = "en_MG"
        en_MH = "en_MH"
        en_MP = "en_MP"
        en_MT = "en_MT"
        en_MU = "en_MU"
        en_MW = "en_MW"
        en_NA = "en_NA"
        en_NG = "en_NG"
        en_NZ = "en_NZ"
        en_PG = "en_PG"
        en_PH = "en_PH"
        en_PK = "en_PK"
        en_PR = "en_PR"
        en_PW = "en_PW"
        en_SB = "en_SB"
        en_SC = "en_SC"
        en_SG = "en_SG"
        en_SL = "en_SL"
        en_SS = "en_SS"
        en_SZ = "en_SZ"
        en_TC = "en_TC"
        en_TO = "en_TO"
        en_TT = "en_TT"
        en_TZ = "en_TZ"
        en_UG = "en_UG"
        en_UM = "en_UM"
        en_US = "en_US"
        en_US_POSIX = "en_US_POSIX"
        en_VC = "en_VC"
        en_VG = "en_VG"
        en_VI = "en_VI"
        en_VU = "en_VU"
        en_WS = "en_WS"
        en_ZA = "en_ZA"
        en_ZM = "en_ZM"
        en_ZW = "en_ZW"
        eo = "eo"
        es = "es"
        es_419 = "es_419"
        es_AR = "es_AR"
        es_BO = "es_BO"
        es_CL = "es_CL"
        es_CO = "es_CO"
        es_CR = "es_CR"
        es_CU = "es_CU"
        es_DO = "es_DO"
        es_EA = "es_EA"
        es_EC = "es_EC"
        es_ES = "es_ES"
        es_GQ = "es_GQ"
        es_GT = "es_GT"
        es_HN = "es_HN"
        es_IC = "es_IC"
        es_MX = "es_MX"
        es_NI = "es_NI"
        es_PA = "es_PA"
        es_PE = "es_PE"
        es_PH = "es_PH"
        es_PR = "es_PR"
        es_PY = "es_PY"
        es_SV = "es_SV"
        es_US = "es_US"
        es_UY = "es_UY"
        es_VE = "es_VE"
        et = "et"
        et_EE = "et_EE"
        eu = "eu"
        eu_ES = "eu_ES"
        ewo = "ewo"
        ewo_CM = "ewo_CM"
        fa = "fa"
        fa_AF = "fa_AF"
        fa_IR = "fa_IR"
        ff = "ff"
        ff_SN = "ff_SN"
        fi = "fi"
        fi_FI = "fi_FI"
        fil = "fil"
        fil_PH = "fil_PH"
        fo = "fo"
        fo_FO = "fo_FO"
        fr = "fr"
        fr_BE = "fr_BE"
        fr_BF = "fr_BF"
        fr_BI = "fr_BI"
        fr_BJ = "fr_BJ"
        fr_BL = "fr_BL"
        fr_CA = "fr_CA"
        fr_CD = "fr_CD"
        fr_CF = "fr_CF"
        fr_CG = "fr_CG"
        fr_CH = "fr_CH"
        fr_CI = "fr_CI"
        fr_CM = "fr_CM"
        fr_DJ = "fr_DJ"
        fr_DZ = "fr_DZ"
        fr_FR = "fr_FR"
        fr_GA = "fr_GA"
        fr_GF = "fr_GF"
        fr_GN = "fr_GN"
        fr_GP = "fr_GP"
        fr_GQ = "fr_GQ"
        fr_HT = "fr_HT"
        fr_KM = "fr_KM"
        fr_LU = "fr_LU"
        fr_MA = "fr_MA"
        fr_MC = "fr_MC"
        fr_MF = "fr_MF"
        fr_MG = "fr_MG"
        fr_ML = "fr_ML"
        fr_MQ = "fr_MQ"
        fr_MR = "fr_MR"
        fr_MU = "fr_MU"
        fr_NC = "fr_NC"
        fr_NE = "fr_NE"
        fr_PF = "fr_PF"
        fr_RE = "fr_RE"
        fr_RW = "fr_RW"
        fr_SC = "fr_SC"
        fr_SN = "fr_SN"
        fr_SY = "fr_SY"
        fr_TD = "fr_TD"
        fr_TG = "fr_TG"
        fr_TN = "fr_TN"
        fr_VU = "fr_VU"
        fr_YT = "fr_YT"
        ga = "ga"
        ga_IE = "ga_IE"
        gl = "gl"
        gl_ES = "gl_ES"
        gsw = "gsw"
        gsw_CH = "gsw_CH"
        gu = "gu"
        gu_IN = "gu_IN"
        guz = "guz"
        guz_KE = "guz_KE"
        gv = "gv"
        gv_GB = "gv_GB"
        ha = "ha"
        ha_Latn = "ha_Latn"
        ha_Latn_GH = "ha_Latn_GH"
        ha_Latn_NE = "ha_Latn_NE"
        ha_Latn_NG = "ha_Latn_NG"
        haw = "haw"
        haw_US = "haw_US"
        he = "he"
        he_IL = "he_IL"
        hi = "hi"
        hi_IN = "hi_IN"
        hr = "hr"
        hr_BA = "hr_BA"
        hr_HR = "hr_HR"
        hu = "hu"
        hu_HU = "hu_HU"
        hy = "hy"
        hy_AM = "hy_AM"
        id = "id"
        id_ID = "id_ID"
        ig = "ig"
        ig_NG = "ig_NG"
        ii = "ii"
        ii_CN = "ii_CN"
        is_ = "is"
        is_IS = "is_IS"
        it = "it"
        it_CH = "it_CH"
        it_IT = "it_IT"
        it_SM = "it_SM"
        ja = "ja"
        ja_JP = "ja_JP"
        jgo = "jgo"
        jgo_CM = "jgo_CM"
        jmc = "jmc"
        jmc_TZ = "jmc_TZ"
        ka = "ka"
        ka_GE = "ka_GE"
        kab = "kab"
        kab_DZ = "kab_DZ"
        kam = "kam"
        kam_KE = "kam_KE"
        kde = "kde"
        kde_TZ = "kde_TZ"
        kea = "kea"
        kea_CV = "kea_CV"
        khq = "khq"
        khq_ML = "khq_ML"
        ki = "ki"
        ki_KE = "ki_KE"
        kk = "kk"
        kk_Cyrl = "kk_Cyrl"
        kk_Cyrl_KZ = "kk_Cyrl_KZ"
        kl = "kl"
        kl_GL = "kl_GL"
        kln = "kln"
        kln_KE = "kln_KE"
        km = "km"
        km_KH = "km_KH"
        kn = "kn"
        kn_IN = "kn_IN"
        ko = "ko"
        ko_KP = "ko_KP"
        ko_KR = "ko_KR"
        kok = "kok"
        kok_IN = "kok_IN"
        ks = "ks"
        ks_Arab = "ks_Arab"
        ks_Arab_IN = "ks_Arab_IN"
        ksb = "ksb"
        ksb_TZ = "ksb_TZ"
        ksf = "ksf"
        ksf_CM = "ksf_CM"
        kw = "kw"
        kw_GB = "kw_GB"
        lag = "lag"
        lag_TZ = "lag_TZ"
        lg = "lg"
        lg_UG = "lg_UG"
        ln = "ln"
        ln_AO = "ln_AO"
        ln_CD = "ln_CD"
        ln_CF = "ln_CF"
        ln_CG = "ln_CG"
        lo = "lo"
        lo_LA = "lo_LA"
        lt = "lt"
        lt_LT = "lt_LT"
        lu = "lu"
        lu_CD = "lu_CD"
        luo = "luo"
        luo_KE = "luo_KE"
        luy = "luy"
        luy_KE = "luy_KE"
        lv = "lv"
        lv_LV = "lv_LV"
        mas = "mas"
        mas_KE = "mas_KE"
        mas_TZ = "mas_TZ"
        mer = "mer"
        mer_KE = "mer_KE"
        mfe = "mfe"
        mfe_MU = "mfe_MU"
        mg = "mg"
        mg_MG = "mg_MG"
        mgh = "mgh"
        mgh_MZ = "mgh_MZ"
        mgo = "mgo"
        mgo_CM = "mgo_CM"
        mk = "mk"
        mk_MK = "mk_MK"
        ml = "ml"
        ml_IN = "ml_IN"
        mr = "mr"
        mr_IN = "mr_IN"
        ms = "ms"
        ms_BN = "ms_BN"
        ms_MY = "ms_MY"
        ms_SG = "ms_SG"
        mt = "mt"
        mt_MT = "mt_MT"
        mua = "mua"
        mua_CM = "mua_CM"
        my = "my"
        my_MM = "my_MM"
        naq = "naq"
        naq_NA = "naq_NA"
        nb = "nb"
        nb_NO = "nb_NO"
        nd = "nd"
        nd_ZW = "nd_ZW"
        ne = "ne"
        ne_IN = "ne_IN"
        ne_NP = "ne_NP"
        nl = "nl"
        nl_AW = "nl_AW"
        nl_BE = "nl_BE"
        nl_CW = "nl_CW"
        nl_NL = "nl_NL"
        nl_SR = "nl_SR"
        nl_SX = "nl_SX"
        nmg = "nmg"
        nmg_CM = "nmg_CM"
        nn = "nn"
        nn_NO = "nn_NO"
        nus = "nus"
        nus_SD = "nus_SD"
        nyn = "nyn"
        nyn_UG = "nyn_UG"
        om = "om"
        om_ET = "om_ET"
        om_KE = "om_KE"
        or_ = "or"
        or_IN = "or_IN"
        pa = "pa"
        pa_Arab = "pa_Arab"
        pa_Arab_PK = "pa_Arab_PK"
        pa_Guru = "pa_Guru"
        pa_Guru_IN = "pa_Guru_IN"
        pl = "pl"
        pl_PL = "pl_PL"
        ps = "ps"
        ps_AF = "ps_AF"
        pt = "pt"
        pt_AO = "pt_AO"
        pt_BR = "pt_BR"
        pt_CV = "pt_CV"
        pt_GW = "pt_GW"
        pt_MO = "pt_MO"
        pt_MZ = "pt_MZ"
        pt_PT = "pt_PT"
        pt_ST = "pt_ST"
        pt_TL = "pt_TL"
        rm = "rm"
        rm_CH = "rm_CH"
        rn = "rn"
        rn_BI = "rn_BI"
        ro = "ro"
        ro_MD = "ro_MD"
        ro_RO = "ro_RO"
        rof = "rof"
        rof_TZ = "rof_TZ"
        ru = "ru"
        ru_BY = "ru_BY"
        ru_KG = "ru_KG"
        ru_KZ = "ru_KZ"
        ru_MD = "ru_MD"
        ru_RU = "ru_RU"
        ru_UA = "ru_UA"
        rw = "rw"
        rw_RW = "rw_RW"
        rwk = "rwk"
        rwk_TZ = "rwk_TZ"
        saq = "saq"
        saq_KE = "saq_KE"
        sbp = "sbp"
        sbp_TZ = "sbp_TZ"
        seh = "seh"
        seh_MZ = "seh_MZ"
        ses = "ses"
        ses_ML = "ses_ML"
        sg = "sg"
        sg_CF = "sg_CF"
        shi = "shi"
        shi_Latn = "shi_Latn"
        shi_Latn_MA = "shi_Latn_MA"
        shi_Tfng = "shi_Tfng"
        shi_Tfng_MA = "shi_Tfng_MA"
        si = "si"
        si_LK = "si_LK"
        sk = "sk"
        sk_SK = "sk_SK"
        sl = "sl"
        sl_SI = "sl_SI"
        sn = "sn"
        sn_ZW = "sn_ZW"
        so = "so"
        so_DJ = "so_DJ"
        so_ET = "so_ET"
        so_KE = "so_KE"
        so_SO = "so_SO"
        sq = "sq"
        sq_AL = "sq_AL"
        sq_MK = "sq_MK"
        sr = "sr"
        sr_Cyrl = "sr_Cyrl"
        sr_Cyrl_BA = "sr_Cyrl_BA"
        sr_Cyrl_ME = "sr_Cyrl_ME"
        sr_Cyrl_RS = "sr_Cyrl_RS"
        sr_Latn = "sr_Latn"
        sr_Latn_BA = "sr_Latn_BA"
        sr_Latn_ME = "sr_Latn_ME"
        sr_Latn_RS = "sr_Latn_RS"
        sv = "sv"
        sv_AX = "sv_AX"
        sv_FI = "sv_FI"
        sv_SE = "sv_SE"
        sw = "sw"
        sw_KE = "sw_KE"
        sw_TZ = "sw_TZ"
        sw_UG = "sw_UG"
        swc = "swc"
        swc_CD = "swc_CD"
        ta = "ta"
        ta_IN = "ta_IN"
        ta_LK = "ta_LK"
        ta_MY = "ta_MY"
        ta_SG = "ta_SG"
        te = "te"
        te_IN = "te_IN"
        teo = "teo"
        teo_KE = "teo_KE"
        teo_UG = "teo_UG"
        th = "th"
        th_TH = "th_TH"
        ti = "ti"
        ti_ER = "ti_ER"
        ti_ET = "ti_ET"
        to = "to"
        to_TO = "to_TO"
        tr = "tr"
        tr_CY = "tr_CY"
        tr_TR = "tr_TR"
        twq = "twq"
        twq_NE = "twq_NE"
        tzm = "tzm"
        tzm_Latn = "tzm_Latn"
        tzm_Latn_MA = "tzm_Latn_MA"
        uk = "uk"
        uk_UA = "uk_UA"
        ur = "ur"
        ur_IN = "ur_IN"
        ur_PK = "ur_PK"
        uz = "uz"
        uz_Arab = "uz_Arab"
        uz_Arab_AF = "uz_Arab_AF"
        uz_Cyrl = "uz_Cyrl"
        uz_Cyrl_UZ = "uz_Cyrl_UZ"
        uz_Latn = "uz_Latn"
        uz_Latn_UZ = "uz_Latn_UZ"
        vai = "vai"
        vai_Latn = "vai_Latn"
        vai_Latn_LR = "vai_Latn_LR"
        vai_Vaii = "vai_Vaii"
        vai_Vaii_LR = "vai_Vaii_LR"
        vi = "vi"
        vi_VN = "vi_VN"
        vun = "vun"
        vun_TZ = "vun_TZ"
        xog = "xog"
        xog_UG = "xog_UG"
        yav = "yav"
        yav_CM = "yav_CM"
        yo = "yo"
        yo_NG = "yo_NG"
        zh = "zh"
        zh_Hans = "zh_Hans"
        zh_Hans_CN = "zh_Hans_CN"
        zh_Hans_HK = "zh_Hans_HK"
        zh_Hans_MO = "zh_Hans_MO"
        zh_Hans_SG = "zh_Hans_SG"
        zh_Hant = "zh_Hant"
        zh_Hant_HK = "zh_Hant_HK"
        zh_Hant_MO = "zh_Hant_MO"
        zh_Hant_TW = "zh_Hant_TW"
        zu = "zu"
        zu_ZA = "zu_ZA"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class MERGE:
    """Enums for properties in the MERGE stage."""

    class DropBadMastersKeepBadMasters(Enum):
        """Enum for the DropBadMastersKeepBadMasters property."""

        keepBadMasters = "keepBadMasters"
        dropBadMasters = "dropBadMasters"

    class NowarnBadMastersWarnBadMasters(Enum):
        """Enum for the NowarnBadMastersWarnBadMasters property."""

        warnBadMasters = "warnBadMasters"
        nowarnBadMasters = "nowarnBadMasters"

    class NowarnBadUpdatesWarnBadUpdates(Enum):
        """Enum for the NowarnBadUpdatesWarnBadUpdates property."""

        warnBadUpdates = "warnBadUpdates"
        nowarnBadUpdates = "nowarnBadUpdates"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class CollationSequence(Enum):
        """Enum for the CollationSequence property."""

        OFF = "OFF"
        af = "af"
        af_NA = "af_NA"
        af_ZA = "af_ZA"
        agq = "agq"
        agq_CM = "agq_CM"
        ak = "ak"
        ak_GH = "ak_GH"
        am = "am"
        am_ET = "am_ET"
        ar = "ar"
        ar_001 = "ar_001"
        ar_AE = "ar_AE"
        ar_BH = "ar_BH"
        ar_DJ = "ar_DJ"
        ar_DZ = "ar_DZ"
        ar_EG = "ar_EG"
        ar_EH = "ar_EH"
        ar_ER = "ar_ER"
        ar_IL = "ar_IL"
        ar_IQ = "ar_IQ"
        ar_JO = "ar_JO"
        ar_KM = "ar_KM"
        ar_KW = "ar_KW"
        ar_LB = "ar_LB"
        ar_LY = "ar_LY"
        ar_MA = "ar_MA"
        ar_MR = "ar_MR"
        ar_OM = "ar_OM"
        ar_PS = "ar_PS"
        ar_QA = "ar_QA"
        ar_SA = "ar_SA"
        ar_SD = "ar_SD"
        ar_SO = "ar_SO"
        ar_SY = "ar_SY"
        ar_TD = "ar_TD"
        ar_TN = "ar_TN"
        ar_YE = "ar_YE"
        as_ = "as"
        as_IN = "as_IN"
        asa = "asa"
        asa_TZ = "asa_TZ"
        az = "az"
        az_Cyrl = "az_Cyrl"
        az_Cyrl_AZ = "az_Cyrl_AZ"
        az_Latn = "az_Latn"
        az_Latn_AZ = "az_Latn_AZ"
        bas = "bas"
        bas_CM = "bas_CM"
        be = "be"
        be_BY = "be_BY"
        bem = "bem"
        bem_ZM = "bem_ZM"
        bez = "bez"
        bez_TZ = "bez_TZ"
        bg = "bg"
        bg_BG = "bg_BG"
        bm = "bm"
        bm_ML = "bm_ML"
        bn = "bn"
        bn_BD = "bn_BD"
        bn_IN = "bn_IN"
        bo = "bo"
        bo_CN = "bo_CN"
        bo_IN = "bo_IN"
        br = "br"
        br_FR = "br_FR"
        brx = "brx"
        brx_IN = "brx_IN"
        bs = "bs"
        bs_Cyrl = "bs_Cyrl"
        bs_Cyrl_BA = "bs_Cyrl_BA"
        bs_Latn = "bs_Latn"
        bs_Latn_BA = "bs_Latn_BA"
        ca = "ca"
        ca_AD = "ca_AD"
        ca_ES = "ca_ES"
        cgg = "cgg"
        cgg_UG = "cgg_UG"
        chr = "chr"
        chr_US = "chr_US"
        cs = "cs"
        cs_CZ = "cs_CZ"
        cy = "cy"
        cy_GB = "cy_GB"
        da = "da"
        da_DK = "da_DK"
        dav = "dav"
        dav_KE = "dav_KE"
        de = "de"
        de_AT = "de_AT"
        de_BE = "de_BE"
        de_CH = "de_CH"
        de_DE = "de_DE"
        de_LI = "de_LI"
        de_LU = "de_LU"
        dje = "dje"
        dje_NE = "dje_NE"
        dua = "dua"
        dua_CM = "dua_CM"
        dyo = "dyo"
        dyo_SN = "dyo_SN"
        dz = "dz"
        dz_BT = "dz_BT"
        ebu = "ebu"
        ebu_KE = "ebu_KE"
        ee = "ee"
        ee_GH = "ee_GH"
        ee_TG = "ee_TG"
        el = "el"
        el_CY = "el_CY"
        el_GR = "el_GR"
        en = "en"
        en_150 = "en_150"
        en_AG = "en_AG"
        en_AS = "en_AS"
        en_AU = "en_AU"
        en_BB = "en_BB"
        en_BE = "en_BE"
        en_BM = "en_BM"
        en_BS = "en_BS"
        en_BW = "en_BW"
        en_BZ = "en_BZ"
        en_CA = "en_CA"
        en_CM = "en_CM"
        en_DM = "en_DM"
        en_FJ = "en_FJ"
        en_FM = "en_FM"
        en_GB = "en_GB"
        en_GD = "en_GD"
        en_GG = "en_GG"
        en_GH = "en_GH"
        en_GI = "en_GI"
        en_GM = "en_GM"
        en_GU = "en_GU"
        en_GY = "en_GY"
        en_HK = "en_HK"
        en_IE = "en_IE"
        en_IM = "en_IM"
        en_IN = "en_IN"
        en_JE = "en_JE"
        en_JM = "en_JM"
        en_KE = "en_KE"
        en_KI = "en_KI"
        en_KN = "en_KN"
        en_KY = "en_KY"
        en_LC = "en_LC"
        en_LR = "en_LR"
        en_LS = "en_LS"
        en_MG = "en_MG"
        en_MH = "en_MH"
        en_MP = "en_MP"
        en_MT = "en_MT"
        en_MU = "en_MU"
        en_MW = "en_MW"
        en_NA = "en_NA"
        en_NG = "en_NG"
        en_NZ = "en_NZ"
        en_PG = "en_PG"
        en_PH = "en_PH"
        en_PK = "en_PK"
        en_PR = "en_PR"
        en_PW = "en_PW"
        en_SB = "en_SB"
        en_SC = "en_SC"
        en_SG = "en_SG"
        en_SL = "en_SL"
        en_SS = "en_SS"
        en_SZ = "en_SZ"
        en_TC = "en_TC"
        en_TO = "en_TO"
        en_TT = "en_TT"
        en_TZ = "en_TZ"
        en_UG = "en_UG"
        en_UM = "en_UM"
        en_US = "en_US"
        en_US_POSIX = "en_US_POSIX"
        en_VC = "en_VC"
        en_VG = "en_VG"
        en_VI = "en_VI"
        en_VU = "en_VU"
        en_WS = "en_WS"
        en_ZA = "en_ZA"
        en_ZM = "en_ZM"
        en_ZW = "en_ZW"
        eo = "eo"
        es = "es"
        es_419 = "es_419"
        es_AR = "es_AR"
        es_BO = "es_BO"
        es_CL = "es_CL"
        es_CO = "es_CO"
        es_CR = "es_CR"
        es_CU = "es_CU"
        es_DO = "es_DO"
        es_EA = "es_EA"
        es_EC = "es_EC"
        es_ES = "es_ES"
        es_GQ = "es_GQ"
        es_GT = "es_GT"
        es_HN = "es_HN"
        es_IC = "es_IC"
        es_MX = "es_MX"
        es_NI = "es_NI"
        es_PA = "es_PA"
        es_PE = "es_PE"
        es_PH = "es_PH"
        es_PR = "es_PR"
        es_PY = "es_PY"
        es_SV = "es_SV"
        es_US = "es_US"
        es_UY = "es_UY"
        es_VE = "es_VE"
        et = "et"
        et_EE = "et_EE"
        eu = "eu"
        eu_ES = "eu_ES"
        ewo = "ewo"
        ewo_CM = "ewo_CM"
        fa = "fa"
        fa_AF = "fa_AF"
        fa_IR = "fa_IR"
        ff = "ff"
        ff_SN = "ff_SN"
        fi = "fi"
        fi_FI = "fi_FI"
        fil = "fil"
        fil_PH = "fil_PH"
        fo = "fo"
        fo_FO = "fo_FO"
        fr = "fr"
        fr_BE = "fr_BE"
        fr_BF = "fr_BF"
        fr_BI = "fr_BI"
        fr_BJ = "fr_BJ"
        fr_BL = "fr_BL"
        fr_CA = "fr_CA"
        fr_CD = "fr_CD"
        fr_CF = "fr_CF"
        fr_CG = "fr_CG"
        fr_CH = "fr_CH"
        fr_CI = "fr_CI"
        fr_CM = "fr_CM"
        fr_DJ = "fr_DJ"
        fr_DZ = "fr_DZ"
        fr_FR = "fr_FR"
        fr_GA = "fr_GA"
        fr_GF = "fr_GF"
        fr_GN = "fr_GN"
        fr_GP = "fr_GP"
        fr_GQ = "fr_GQ"
        fr_HT = "fr_HT"
        fr_KM = "fr_KM"
        fr_LU = "fr_LU"
        fr_MA = "fr_MA"
        fr_MC = "fr_MC"
        fr_MF = "fr_MF"
        fr_MG = "fr_MG"
        fr_ML = "fr_ML"
        fr_MQ = "fr_MQ"
        fr_MR = "fr_MR"
        fr_MU = "fr_MU"
        fr_NC = "fr_NC"
        fr_NE = "fr_NE"
        fr_PF = "fr_PF"
        fr_RE = "fr_RE"
        fr_RW = "fr_RW"
        fr_SC = "fr_SC"
        fr_SN = "fr_SN"
        fr_SY = "fr_SY"
        fr_TD = "fr_TD"
        fr_TG = "fr_TG"
        fr_TN = "fr_TN"
        fr_VU = "fr_VU"
        fr_YT = "fr_YT"
        ga = "ga"
        ga_IE = "ga_IE"
        gl = "gl"
        gl_ES = "gl_ES"
        gsw = "gsw"
        gsw_CH = "gsw_CH"
        gu = "gu"
        gu_IN = "gu_IN"
        guz = "guz"
        guz_KE = "guz_KE"
        gv = "gv"
        gv_GB = "gv_GB"
        ha = "ha"
        ha_Latn = "ha_Latn"
        ha_Latn_GH = "ha_Latn_GH"
        ha_Latn_NE = "ha_Latn_NE"
        ha_Latn_NG = "ha_Latn_NG"
        haw = "haw"
        haw_US = "haw_US"
        he = "he"
        he_IL = "he_IL"
        hi = "hi"
        hi_IN = "hi_IN"
        hr = "hr"
        hr_BA = "hr_BA"
        hr_HR = "hr_HR"
        hu = "hu"
        hu_HU = "hu_HU"
        hy = "hy"
        hy_AM = "hy_AM"
        id = "id"
        id_ID = "id_ID"
        ig = "ig"
        ig_NG = "ig_NG"
        ii = "ii"
        ii_CN = "ii_CN"
        is_ = "is"
        is_IS = "is_IS"
        it = "it"
        it_CH = "it_CH"
        it_IT = "it_IT"
        it_SM = "it_SM"
        ja = "ja"
        ja_JP = "ja_JP"
        jgo = "jgo"
        jgo_CM = "jgo_CM"
        jmc = "jmc"
        jmc_TZ = "jmc_TZ"
        ka = "ka"
        ka_GE = "ka_GE"
        kab = "kab"
        kab_DZ = "kab_DZ"
        kam = "kam"
        kam_KE = "kam_KE"
        kde = "kde"
        kde_TZ = "kde_TZ"
        kea = "kea"
        kea_CV = "kea_CV"
        khq = "khq"
        khq_ML = "khq_ML"
        ki = "ki"
        ki_KE = "ki_KE"
        kk = "kk"
        kk_Cyrl = "kk_Cyrl"
        kk_Cyrl_KZ = "kk_Cyrl_KZ"
        kl = "kl"
        kl_GL = "kl_GL"
        kln = "kln"
        kln_KE = "kln_KE"
        km = "km"
        km_KH = "km_KH"
        kn = "kn"
        kn_IN = "kn_IN"
        ko = "ko"
        ko_KP = "ko_KP"
        ko_KR = "ko_KR"
        kok = "kok"
        kok_IN = "kok_IN"
        ks = "ks"
        ks_Arab = "ks_Arab"
        ks_Arab_IN = "ks_Arab_IN"
        ksb = "ksb"
        ksb_TZ = "ksb_TZ"
        ksf = "ksf"
        ksf_CM = "ksf_CM"
        kw = "kw"
        kw_GB = "kw_GB"
        lag = "lag"
        lag_TZ = "lag_TZ"
        lg = "lg"
        lg_UG = "lg_UG"
        ln = "ln"
        ln_AO = "ln_AO"
        ln_CD = "ln_CD"
        ln_CF = "ln_CF"
        ln_CG = "ln_CG"
        lo = "lo"
        lo_LA = "lo_LA"
        lt = "lt"
        lt_LT = "lt_LT"
        lu = "lu"
        lu_CD = "lu_CD"
        luo = "luo"
        luo_KE = "luo_KE"
        luy = "luy"
        luy_KE = "luy_KE"
        lv = "lv"
        lv_LV = "lv_LV"
        mas = "mas"
        mas_KE = "mas_KE"
        mas_TZ = "mas_TZ"
        mer = "mer"
        mer_KE = "mer_KE"
        mfe = "mfe"
        mfe_MU = "mfe_MU"
        mg = "mg"
        mg_MG = "mg_MG"
        mgh = "mgh"
        mgh_MZ = "mgh_MZ"
        mgo = "mgo"
        mgo_CM = "mgo_CM"
        mk = "mk"
        mk_MK = "mk_MK"
        ml = "ml"
        ml_IN = "ml_IN"
        mr = "mr"
        mr_IN = "mr_IN"
        ms = "ms"
        ms_BN = "ms_BN"
        ms_MY = "ms_MY"
        ms_SG = "ms_SG"
        mt = "mt"
        mt_MT = "mt_MT"
        mua = "mua"
        mua_CM = "mua_CM"
        my = "my"
        my_MM = "my_MM"
        naq = "naq"
        naq_NA = "naq_NA"
        nb = "nb"
        nb_NO = "nb_NO"
        nd = "nd"
        nd_ZW = "nd_ZW"
        ne = "ne"
        ne_IN = "ne_IN"
        ne_NP = "ne_NP"
        nl = "nl"
        nl_AW = "nl_AW"
        nl_BE = "nl_BE"
        nl_CW = "nl_CW"
        nl_NL = "nl_NL"
        nl_SR = "nl_SR"
        nl_SX = "nl_SX"
        nmg = "nmg"
        nmg_CM = "nmg_CM"
        nn = "nn"
        nn_NO = "nn_NO"
        nus = "nus"
        nus_SD = "nus_SD"
        nyn = "nyn"
        nyn_UG = "nyn_UG"
        om = "om"
        om_ET = "om_ET"
        om_KE = "om_KE"
        or_ = "or"
        or_IN = "or_IN"
        pa = "pa"
        pa_Arab = "pa_Arab"
        pa_Arab_PK = "pa_Arab_PK"
        pa_Guru = "pa_Guru"
        pa_Guru_IN = "pa_Guru_IN"
        pl = "pl"
        pl_PL = "pl_PL"
        ps = "ps"
        ps_AF = "ps_AF"
        pt = "pt"
        pt_AO = "pt_AO"
        pt_BR = "pt_BR"
        pt_CV = "pt_CV"
        pt_GW = "pt_GW"
        pt_MO = "pt_MO"
        pt_MZ = "pt_MZ"
        pt_PT = "pt_PT"
        pt_ST = "pt_ST"
        pt_TL = "pt_TL"
        rm = "rm"
        rm_CH = "rm_CH"
        rn = "rn"
        rn_BI = "rn_BI"
        ro = "ro"
        ro_MD = "ro_MD"
        ro_RO = "ro_RO"
        rof = "rof"
        rof_TZ = "rof_TZ"
        ru = "ru"
        ru_BY = "ru_BY"
        ru_KG = "ru_KG"
        ru_KZ = "ru_KZ"
        ru_MD = "ru_MD"
        ru_RU = "ru_RU"
        ru_UA = "ru_UA"
        rw = "rw"
        rw_RW = "rw_RW"
        rwk = "rwk"
        rwk_TZ = "rwk_TZ"
        saq = "saq"
        saq_KE = "saq_KE"
        sbp = "sbp"
        sbp_TZ = "sbp_TZ"
        seh = "seh"
        seh_MZ = "seh_MZ"
        ses = "ses"
        ses_ML = "ses_ML"
        sg = "sg"
        sg_CF = "sg_CF"
        shi = "shi"
        shi_Latn = "shi_Latn"
        shi_Latn_MA = "shi_Latn_MA"
        shi_Tfng = "shi_Tfng"
        shi_Tfng_MA = "shi_Tfng_MA"
        si = "si"
        si_LK = "si_LK"
        sk = "sk"
        sk_SK = "sk_SK"
        sl = "sl"
        sl_SI = "sl_SI"
        sn = "sn"
        sn_ZW = "sn_ZW"
        so = "so"
        so_DJ = "so_DJ"
        so_ET = "so_ET"
        so_KE = "so_KE"
        so_SO = "so_SO"
        sq = "sq"
        sq_AL = "sq_AL"
        sq_MK = "sq_MK"
        sr = "sr"
        sr_Cyrl = "sr_Cyrl"
        sr_Cyrl_BA = "sr_Cyrl_BA"
        sr_Cyrl_ME = "sr_Cyrl_ME"
        sr_Cyrl_RS = "sr_Cyrl_RS"
        sr_Latn = "sr_Latn"
        sr_Latn_BA = "sr_Latn_BA"
        sr_Latn_ME = "sr_Latn_ME"
        sr_Latn_RS = "sr_Latn_RS"
        sv = "sv"
        sv_AX = "sv_AX"
        sv_FI = "sv_FI"
        sv_SE = "sv_SE"
        sw = "sw"
        sw_KE = "sw_KE"
        sw_TZ = "sw_TZ"
        sw_UG = "sw_UG"
        swc = "swc"
        swc_CD = "swc_CD"
        ta = "ta"
        ta_IN = "ta_IN"
        ta_LK = "ta_LK"
        ta_MY = "ta_MY"
        ta_SG = "ta_SG"
        te = "te"
        te_IN = "te_IN"
        teo = "teo"
        teo_KE = "teo_KE"
        teo_UG = "teo_UG"
        th = "th"
        th_TH = "th_TH"
        ti = "ti"
        ti_ER = "ti_ER"
        ti_ET = "ti_ET"
        to = "to"
        to_TO = "to_TO"
        tr = "tr"
        tr_CY = "tr_CY"
        tr_TR = "tr_TR"
        twq = "twq"
        twq_NE = "twq_NE"
        tzm = "tzm"
        tzm_Latn = "tzm_Latn"
        tzm_Latn_MA = "tzm_Latn_MA"
        uk = "uk"
        uk_UA = "uk_UA"
        ur = "ur"
        ur_IN = "ur_IN"
        ur_PK = "ur_PK"
        uz = "uz"
        uz_Arab = "uz_Arab"
        uz_Arab_AF = "uz_Arab_AF"
        uz_Cyrl = "uz_Cyrl"
        uz_Cyrl_UZ = "uz_Cyrl_UZ"
        uz_Latn = "uz_Latn"
        uz_Latn_UZ = "uz_Latn_UZ"
        vai = "vai"
        vai_Latn = "vai_Latn"
        vai_Latn_LR = "vai_Latn_LR"
        vai_Vaii = "vai_Vaii"
        vai_Vaii_LR = "vai_Vaii_LR"
        vi = "vi"
        vi_VN = "vi_VN"
        vun = "vun"
        vun_TZ = "vun_TZ"
        xog = "xog"
        xog_UG = "xog_UG"
        yav = "yav"
        yav_CM = "yav_CM"
        yo = "yo"
        yo_NG = "yo_NG"
        zh = "zh"
        zh_Hans = "zh_Hans"
        zh_Hans_CN = "zh_Hans_CN"
        zh_Hans_HK = "zh_Hans_HK"
        zh_Hans_MO = "zh_Hans_MO"
        zh_Hans_SG = "zh_Hans_SG"
        zh_Hant = "zh_Hant"
        zh_Hant_HK = "zh_Hant_HK"
        zh_Hant_MO = "zh_Hant_MO"
        zh_Hant_TW = "zh_Hant_TW"
        zu = "zu"
        zu_ZA = "zu_ZA"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class COMPARE:
    """Enums for properties in the COMPARE stage."""

    class AbortOnDifference(Enum):
        """Enum for the AbortOnDifference property."""

        false = " "
        true = "abortOnDifference"

    class WarnRecordCountMismatch(Enum):
        """Enum for the WarnRecordCountMismatch property."""

        false = " "
        true = "warnRecordCountMismatch"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class CollationSequence(Enum):
        """Enum for the CollationSequence property."""

        OFF = "OFF"
        af = "af"
        af_NA = "af_NA"
        af_ZA = "af_ZA"
        agq = "agq"
        agq_CM = "agq_CM"
        ak = "ak"
        ak_GH = "ak_GH"
        am = "am"
        am_ET = "am_ET"
        ar = "ar"
        ar_001 = "ar_001"
        ar_AE = "ar_AE"
        ar_BH = "ar_BH"
        ar_DJ = "ar_DJ"
        ar_DZ = "ar_DZ"
        ar_EG = "ar_EG"
        ar_EH = "ar_EH"
        ar_ER = "ar_ER"
        ar_IL = "ar_IL"
        ar_IQ = "ar_IQ"
        ar_JO = "ar_JO"
        ar_KM = "ar_KM"
        ar_KW = "ar_KW"
        ar_LB = "ar_LB"
        ar_LY = "ar_LY"
        ar_MA = "ar_MA"
        ar_MR = "ar_MR"
        ar_OM = "ar_OM"
        ar_PS = "ar_PS"
        ar_QA = "ar_QA"
        ar_SA = "ar_SA"
        ar_SD = "ar_SD"
        ar_SO = "ar_SO"
        ar_SY = "ar_SY"
        ar_TD = "ar_TD"
        ar_TN = "ar_TN"
        ar_YE = "ar_YE"
        as_ = "as"
        as_IN = "as_IN"
        asa = "asa"
        asa_TZ = "asa_TZ"
        az = "az"
        az_Cyrl = "az_Cyrl"
        az_Cyrl_AZ = "az_Cyrl_AZ"
        az_Latn = "az_Latn"
        az_Latn_AZ = "az_Latn_AZ"
        bas = "bas"
        bas_CM = "bas_CM"
        be = "be"
        be_BY = "be_BY"
        bem = "bem"
        bem_ZM = "bem_ZM"
        bez = "bez"
        bez_TZ = "bez_TZ"
        bg = "bg"
        bg_BG = "bg_BG"
        bm = "bm"
        bm_ML = "bm_ML"
        bn = "bn"
        bn_BD = "bn_BD"
        bn_IN = "bn_IN"
        bo = "bo"
        bo_CN = "bo_CN"
        bo_IN = "bo_IN"
        br = "br"
        br_FR = "br_FR"
        brx = "brx"
        brx_IN = "brx_IN"
        bs = "bs"
        bs_Cyrl = "bs_Cyrl"
        bs_Cyrl_BA = "bs_Cyrl_BA"
        bs_Latn = "bs_Latn"
        bs_Latn_BA = "bs_Latn_BA"
        ca = "ca"
        ca_AD = "ca_AD"
        ca_ES = "ca_ES"
        cgg = "cgg"
        cgg_UG = "cgg_UG"
        chr = "chr"
        chr_US = "chr_US"
        cs = "cs"
        cs_CZ = "cs_CZ"
        cy = "cy"
        cy_GB = "cy_GB"
        da = "da"
        da_DK = "da_DK"
        dav = "dav"
        dav_KE = "dav_KE"
        de = "de"
        de_AT = "de_AT"
        de_BE = "de_BE"
        de_CH = "de_CH"
        de_DE = "de_DE"
        de_LI = "de_LI"
        de_LU = "de_LU"
        dje = "dje"
        dje_NE = "dje_NE"
        dua = "dua"
        dua_CM = "dua_CM"
        dyo = "dyo"
        dyo_SN = "dyo_SN"
        dz = "dz"
        dz_BT = "dz_BT"
        ebu = "ebu"
        ebu_KE = "ebu_KE"
        ee = "ee"
        ee_GH = "ee_GH"
        ee_TG = "ee_TG"
        el = "el"
        el_CY = "el_CY"
        el_GR = "el_GR"
        en = "en"
        en_150 = "en_150"
        en_AG = "en_AG"
        en_AS = "en_AS"
        en_AU = "en_AU"
        en_BB = "en_BB"
        en_BE = "en_BE"
        en_BM = "en_BM"
        en_BS = "en_BS"
        en_BW = "en_BW"
        en_BZ = "en_BZ"
        en_CA = "en_CA"
        en_CM = "en_CM"
        en_DM = "en_DM"
        en_FJ = "en_FJ"
        en_FM = "en_FM"
        en_GB = "en_GB"
        en_GD = "en_GD"
        en_GG = "en_GG"
        en_GH = "en_GH"
        en_GI = "en_GI"
        en_GM = "en_GM"
        en_GU = "en_GU"
        en_GY = "en_GY"
        en_HK = "en_HK"
        en_IE = "en_IE"
        en_IM = "en_IM"
        en_IN = "en_IN"
        en_JE = "en_JE"
        en_JM = "en_JM"
        en_KE = "en_KE"
        en_KI = "en_KI"
        en_KN = "en_KN"
        en_KY = "en_KY"
        en_LC = "en_LC"
        en_LR = "en_LR"
        en_LS = "en_LS"
        en_MG = "en_MG"
        en_MH = "en_MH"
        en_MP = "en_MP"
        en_MT = "en_MT"
        en_MU = "en_MU"
        en_MW = "en_MW"
        en_NA = "en_NA"
        en_NG = "en_NG"
        en_NZ = "en_NZ"
        en_PG = "en_PG"
        en_PH = "en_PH"
        en_PK = "en_PK"
        en_PR = "en_PR"
        en_PW = "en_PW"
        en_SB = "en_SB"
        en_SC = "en_SC"
        en_SG = "en_SG"
        en_SL = "en_SL"
        en_SS = "en_SS"
        en_SZ = "en_SZ"
        en_TC = "en_TC"
        en_TO = "en_TO"
        en_TT = "en_TT"
        en_TZ = "en_TZ"
        en_UG = "en_UG"
        en_UM = "en_UM"
        en_US = "en_US"
        en_US_POSIX = "en_US_POSIX"
        en_VC = "en_VC"
        en_VG = "en_VG"
        en_VI = "en_VI"
        en_VU = "en_VU"
        en_WS = "en_WS"
        en_ZA = "en_ZA"
        en_ZM = "en_ZM"
        en_ZW = "en_ZW"
        eo = "eo"
        es = "es"
        es_419 = "es_419"
        es_AR = "es_AR"
        es_BO = "es_BO"
        es_CL = "es_CL"
        es_CO = "es_CO"
        es_CR = "es_CR"
        es_CU = "es_CU"
        es_DO = "es_DO"
        es_EA = "es_EA"
        es_EC = "es_EC"
        es_ES = "es_ES"
        es_GQ = "es_GQ"
        es_GT = "es_GT"
        es_HN = "es_HN"
        es_IC = "es_IC"
        es_MX = "es_MX"
        es_NI = "es_NI"
        es_PA = "es_PA"
        es_PE = "es_PE"
        es_PH = "es_PH"
        es_PR = "es_PR"
        es_PY = "es_PY"
        es_SV = "es_SV"
        es_US = "es_US"
        es_UY = "es_UY"
        es_VE = "es_VE"
        et = "et"
        et_EE = "et_EE"
        eu = "eu"
        eu_ES = "eu_ES"
        ewo = "ewo"
        ewo_CM = "ewo_CM"
        fa = "fa"
        fa_AF = "fa_AF"
        fa_IR = "fa_IR"
        ff = "ff"
        ff_SN = "ff_SN"
        fi = "fi"
        fi_FI = "fi_FI"
        fil = "fil"
        fil_PH = "fil_PH"
        fo = "fo"
        fo_FO = "fo_FO"
        fr = "fr"
        fr_BE = "fr_BE"
        fr_BF = "fr_BF"
        fr_BI = "fr_BI"
        fr_BJ = "fr_BJ"
        fr_BL = "fr_BL"
        fr_CA = "fr_CA"
        fr_CD = "fr_CD"
        fr_CF = "fr_CF"
        fr_CG = "fr_CG"
        fr_CH = "fr_CH"
        fr_CI = "fr_CI"
        fr_CM = "fr_CM"
        fr_DJ = "fr_DJ"
        fr_DZ = "fr_DZ"
        fr_FR = "fr_FR"
        fr_GA = "fr_GA"
        fr_GF = "fr_GF"
        fr_GN = "fr_GN"
        fr_GP = "fr_GP"
        fr_GQ = "fr_GQ"
        fr_HT = "fr_HT"
        fr_KM = "fr_KM"
        fr_LU = "fr_LU"
        fr_MA = "fr_MA"
        fr_MC = "fr_MC"
        fr_MF = "fr_MF"
        fr_MG = "fr_MG"
        fr_ML = "fr_ML"
        fr_MQ = "fr_MQ"
        fr_MR = "fr_MR"
        fr_MU = "fr_MU"
        fr_NC = "fr_NC"
        fr_NE = "fr_NE"
        fr_PF = "fr_PF"
        fr_RE = "fr_RE"
        fr_RW = "fr_RW"
        fr_SC = "fr_SC"
        fr_SN = "fr_SN"
        fr_SY = "fr_SY"
        fr_TD = "fr_TD"
        fr_TG = "fr_TG"
        fr_TN = "fr_TN"
        fr_VU = "fr_VU"
        fr_YT = "fr_YT"
        ga = "ga"
        ga_IE = "ga_IE"
        gl = "gl"
        gl_ES = "gl_ES"
        gsw = "gsw"
        gsw_CH = "gsw_CH"
        gu = "gu"
        gu_IN = "gu_IN"
        guz = "guz"
        guz_KE = "guz_KE"
        gv = "gv"
        gv_GB = "gv_GB"
        ha = "ha"
        ha_Latn = "ha_Latn"
        ha_Latn_GH = "ha_Latn_GH"
        ha_Latn_NE = "ha_Latn_NE"
        ha_Latn_NG = "ha_Latn_NG"
        haw = "haw"
        haw_US = "haw_US"
        he = "he"
        he_IL = "he_IL"
        hi = "hi"
        hi_IN = "hi_IN"
        hr = "hr"
        hr_BA = "hr_BA"
        hr_HR = "hr_HR"
        hu = "hu"
        hu_HU = "hu_HU"
        hy = "hy"
        hy_AM = "hy_AM"
        id = "id"
        id_ID = "id_ID"
        ig = "ig"
        ig_NG = "ig_NG"
        ii = "ii"
        ii_CN = "ii_CN"
        is_ = "is"
        is_IS = "is_IS"
        it = "it"
        it_CH = "it_CH"
        it_IT = "it_IT"
        it_SM = "it_SM"
        ja = "ja"
        ja_JP = "ja_JP"
        jgo = "jgo"
        jgo_CM = "jgo_CM"
        jmc = "jmc"
        jmc_TZ = "jmc_TZ"
        ka = "ka"
        ka_GE = "ka_GE"
        kab = "kab"
        kab_DZ = "kab_DZ"
        kam = "kam"
        kam_KE = "kam_KE"
        kde = "kde"
        kde_TZ = "kde_TZ"
        kea = "kea"
        kea_CV = "kea_CV"
        khq = "khq"
        khq_ML = "khq_ML"
        ki = "ki"
        ki_KE = "ki_KE"
        kk = "kk"
        kk_Cyrl = "kk_Cyrl"
        kk_Cyrl_KZ = "kk_Cyrl_KZ"
        kl = "kl"
        kl_GL = "kl_GL"
        kln = "kln"
        kln_KE = "kln_KE"
        km = "km"
        km_KH = "km_KH"
        kn = "kn"
        kn_IN = "kn_IN"
        ko = "ko"
        ko_KP = "ko_KP"
        ko_KR = "ko_KR"
        kok = "kok"
        kok_IN = "kok_IN"
        ks = "ks"
        ks_Arab = "ks_Arab"
        ks_Arab_IN = "ks_Arab_IN"
        ksb = "ksb"
        ksb_TZ = "ksb_TZ"
        ksf = "ksf"
        ksf_CM = "ksf_CM"
        kw = "kw"
        kw_GB = "kw_GB"
        lag = "lag"
        lag_TZ = "lag_TZ"
        lg = "lg"
        lg_UG = "lg_UG"
        ln = "ln"
        ln_AO = "ln_AO"
        ln_CD = "ln_CD"
        ln_CF = "ln_CF"
        ln_CG = "ln_CG"
        lo = "lo"
        lo_LA = "lo_LA"
        lt = "lt"
        lt_LT = "lt_LT"
        lu = "lu"
        lu_CD = "lu_CD"
        luo = "luo"
        luo_KE = "luo_KE"
        luy = "luy"
        luy_KE = "luy_KE"
        lv = "lv"
        lv_LV = "lv_LV"
        mas = "mas"
        mas_KE = "mas_KE"
        mas_TZ = "mas_TZ"
        mer = "mer"
        mer_KE = "mer_KE"
        mfe = "mfe"
        mfe_MU = "mfe_MU"
        mg = "mg"
        mg_MG = "mg_MG"
        mgh = "mgh"
        mgh_MZ = "mgh_MZ"
        mgo = "mgo"
        mgo_CM = "mgo_CM"
        mk = "mk"
        mk_MK = "mk_MK"
        ml = "ml"
        ml_IN = "ml_IN"
        mr = "mr"
        mr_IN = "mr_IN"
        ms = "ms"
        ms_BN = "ms_BN"
        ms_MY = "ms_MY"
        ms_SG = "ms_SG"
        mt = "mt"
        mt_MT = "mt_MT"
        mua = "mua"
        mua_CM = "mua_CM"
        my = "my"
        my_MM = "my_MM"
        naq = "naq"
        naq_NA = "naq_NA"
        nb = "nb"
        nb_NO = "nb_NO"
        nd = "nd"
        nd_ZW = "nd_ZW"
        ne = "ne"
        ne_IN = "ne_IN"
        ne_NP = "ne_NP"
        nl = "nl"
        nl_AW = "nl_AW"
        nl_BE = "nl_BE"
        nl_CW = "nl_CW"
        nl_NL = "nl_NL"
        nl_SR = "nl_SR"
        nl_SX = "nl_SX"
        nmg = "nmg"
        nmg_CM = "nmg_CM"
        nn = "nn"
        nn_NO = "nn_NO"
        nus = "nus"
        nus_SD = "nus_SD"
        nyn = "nyn"
        nyn_UG = "nyn_UG"
        om = "om"
        om_ET = "om_ET"
        om_KE = "om_KE"
        or_ = "or"
        or_IN = "or_IN"
        pa = "pa"
        pa_Arab = "pa_Arab"
        pa_Arab_PK = "pa_Arab_PK"
        pa_Guru = "pa_Guru"
        pa_Guru_IN = "pa_Guru_IN"
        pl = "pl"
        pl_PL = "pl_PL"
        ps = "ps"
        ps_AF = "ps_AF"
        pt = "pt"
        pt_AO = "pt_AO"
        pt_BR = "pt_BR"
        pt_CV = "pt_CV"
        pt_GW = "pt_GW"
        pt_MO = "pt_MO"
        pt_MZ = "pt_MZ"
        pt_PT = "pt_PT"
        pt_ST = "pt_ST"
        pt_TL = "pt_TL"
        rm = "rm"
        rm_CH = "rm_CH"
        rn = "rn"
        rn_BI = "rn_BI"
        ro = "ro"
        ro_MD = "ro_MD"
        ro_RO = "ro_RO"
        rof = "rof"
        rof_TZ = "rof_TZ"
        ru = "ru"
        ru_BY = "ru_BY"
        ru_KG = "ru_KG"
        ru_KZ = "ru_KZ"
        ru_MD = "ru_MD"
        ru_RU = "ru_RU"
        ru_UA = "ru_UA"
        rw = "rw"
        rw_RW = "rw_RW"
        rwk = "rwk"
        rwk_TZ = "rwk_TZ"
        saq = "saq"
        saq_KE = "saq_KE"
        sbp = "sbp"
        sbp_TZ = "sbp_TZ"
        seh = "seh"
        seh_MZ = "seh_MZ"
        ses = "ses"
        ses_ML = "ses_ML"
        sg = "sg"
        sg_CF = "sg_CF"
        shi = "shi"
        shi_Latn = "shi_Latn"
        shi_Latn_MA = "shi_Latn_MA"
        shi_Tfng = "shi_Tfng"
        shi_Tfng_MA = "shi_Tfng_MA"
        si = "si"
        si_LK = "si_LK"
        sk = "sk"
        sk_SK = "sk_SK"
        sl = "sl"
        sl_SI = "sl_SI"
        sn = "sn"
        sn_ZW = "sn_ZW"
        so = "so"
        so_DJ = "so_DJ"
        so_ET = "so_ET"
        so_KE = "so_KE"
        so_SO = "so_SO"
        sq = "sq"
        sq_AL = "sq_AL"
        sq_MK = "sq_MK"
        sr = "sr"
        sr_Cyrl = "sr_Cyrl"
        sr_Cyrl_BA = "sr_Cyrl_BA"
        sr_Cyrl_ME = "sr_Cyrl_ME"
        sr_Cyrl_RS = "sr_Cyrl_RS"
        sr_Latn = "sr_Latn"
        sr_Latn_BA = "sr_Latn_BA"
        sr_Latn_ME = "sr_Latn_ME"
        sr_Latn_RS = "sr_Latn_RS"
        sv = "sv"
        sv_AX = "sv_AX"
        sv_FI = "sv_FI"
        sv_SE = "sv_SE"
        sw = "sw"
        sw_KE = "sw_KE"
        sw_TZ = "sw_TZ"
        sw_UG = "sw_UG"
        swc = "swc"
        swc_CD = "swc_CD"
        ta = "ta"
        ta_IN = "ta_IN"
        ta_LK = "ta_LK"
        ta_MY = "ta_MY"
        ta_SG = "ta_SG"
        te = "te"
        te_IN = "te_IN"
        teo = "teo"
        teo_KE = "teo_KE"
        teo_UG = "teo_UG"
        th = "th"
        th_TH = "th_TH"
        ti = "ti"
        ti_ER = "ti_ER"
        ti_ET = "ti_ET"
        to = "to"
        to_TO = "to_TO"
        tr = "tr"
        tr_CY = "tr_CY"
        tr_TR = "tr_TR"
        twq = "twq"
        twq_NE = "twq_NE"
        tzm = "tzm"
        tzm_Latn = "tzm_Latn"
        tzm_Latn_MA = "tzm_Latn_MA"
        uk = "uk"
        uk_UA = "uk_UA"
        ur = "ur"
        ur_IN = "ur_IN"
        ur_PK = "ur_PK"
        uz = "uz"
        uz_Arab = "uz_Arab"
        uz_Arab_AF = "uz_Arab_AF"
        uz_Cyrl = "uz_Cyrl"
        uz_Cyrl_UZ = "uz_Cyrl_UZ"
        uz_Latn = "uz_Latn"
        uz_Latn_UZ = "uz_Latn_UZ"
        vai = "vai"
        vai_Latn = "vai_Latn"
        vai_Latn_LR = "vai_Latn_LR"
        vai_Vaii = "vai_Vaii"
        vai_Vaii_LR = "vai_Vaii_LR"
        vi = "vi"
        vi_VN = "vi_VN"
        vun = "vun"
        vun_TZ = "vun_TZ"
        xog = "xog"
        xog_UG = "xog_UG"
        yav = "yav"
        yav_CM = "yav_CM"
        yo = "yo"
        yo_NG = "yo_NG"
        zh = "zh"
        zh_Hans = "zh_Hans"
        zh_Hans_CN = "zh_Hans_CN"
        zh_Hans_HK = "zh_Hans_HK"
        zh_Hans_MO = "zh_Hans_MO"
        zh_Hans_SG = "zh_Hans_SG"
        zh_Hant = "zh_Hant"
        zh_Hant_HK = "zh_Hant_HK"
        zh_Hant_MO = "zh_Hant_MO"
        zh_Hant_TW = "zh_Hant_TW"
        zu = "zu"
        zu_ZA = "zu_ZA"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class AGGREGATOR:
    """Enums for properties in the AGGREGATOR stage."""

    class Method(Enum):
        """Enum for the Method property."""

        hash = "hash"
        sort = "sort"

    class NulRes(Enum):
        """Enum for the NulRes property."""

        false = " "
        true = "nul_res"

    class Selection(Enum):
        """Enum for the Selection property."""

        reduce = "reduce"
        rereduce = "rereduce"
        countField = "countField"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_set = -2
        clear = 0
        set = 1

    class CollationSequence(Enum):
        """Enum for the CollationSequence property."""

        OFF = "OFF"
        af = "af"
        af_NA = "af_NA"
        af_ZA = "af_ZA"
        agq = "agq"
        agq_CM = "agq_CM"
        ak = "ak"
        ak_GH = "ak_GH"
        am = "am"
        am_ET = "am_ET"
        ar = "ar"
        ar_001 = "ar_001"
        ar_AE = "ar_AE"
        ar_BH = "ar_BH"
        ar_DJ = "ar_DJ"
        ar_DZ = "ar_DZ"
        ar_EG = "ar_EG"
        ar_EH = "ar_EH"
        ar_ER = "ar_ER"
        ar_IL = "ar_IL"
        ar_IQ = "ar_IQ"
        ar_JO = "ar_JO"
        ar_KM = "ar_KM"
        ar_KW = "ar_KW"
        ar_LB = "ar_LB"
        ar_LY = "ar_LY"
        ar_MA = "ar_MA"
        ar_MR = "ar_MR"
        ar_OM = "ar_OM"
        ar_PS = "ar_PS"
        ar_QA = "ar_QA"
        ar_SA = "ar_SA"
        ar_SD = "ar_SD"
        ar_SO = "ar_SO"
        ar_SY = "ar_SY"
        ar_TD = "ar_TD"
        ar_TN = "ar_TN"
        ar_YE = "ar_YE"
        as_ = "as"
        as_IN = "as_IN"
        asa = "asa"
        asa_TZ = "asa_TZ"
        az = "az"
        az_Cyrl = "az_Cyrl"
        az_Cyrl_AZ = "az_Cyrl_AZ"
        az_Latn = "az_Latn"
        az_Latn_AZ = "az_Latn_AZ"
        bas = "bas"
        bas_CM = "bas_CM"
        be = "be"
        be_BY = "be_BY"
        bem = "bem"
        bem_ZM = "bem_ZM"
        bez = "bez"
        bez_TZ = "bez_TZ"
        bg = "bg"
        bg_BG = "bg_BG"
        bm = "bm"
        bm_ML = "bm_ML"
        bn = "bn"
        bn_BD = "bn_BD"
        bn_IN = "bn_IN"
        bo = "bo"
        bo_CN = "bo_CN"
        bo_IN = "bo_IN"
        br = "br"
        br_FR = "br_FR"
        brx = "brx"
        brx_IN = "brx_IN"
        bs = "bs"
        bs_Cyrl = "bs_Cyrl"
        bs_Cyrl_BA = "bs_Cyrl_BA"
        bs_Latn = "bs_Latn"
        bs_Latn_BA = "bs_Latn_BA"
        ca = "ca"
        ca_AD = "ca_AD"
        ca_ES = "ca_ES"
        cgg = "cgg"
        cgg_UG = "cgg_UG"
        chr = "chr"
        chr_US = "chr_US"
        cs = "cs"
        cs_CZ = "cs_CZ"
        cy = "cy"
        cy_GB = "cy_GB"
        da = "da"
        da_DK = "da_DK"
        dav = "dav"
        dav_KE = "dav_KE"
        de = "de"
        de_AT = "de_AT"
        de_BE = "de_BE"
        de_CH = "de_CH"
        de_DE = "de_DE"
        de_LI = "de_LI"
        de_LU = "de_LU"
        dje = "dje"
        dje_NE = "dje_NE"
        dua = "dua"
        dua_CM = "dua_CM"
        dyo = "dyo"
        dyo_SN = "dyo_SN"
        dz = "dz"
        dz_BT = "dz_BT"
        ebu = "ebu"
        ebu_KE = "ebu_KE"
        ee = "ee"
        ee_GH = "ee_GH"
        ee_TG = "ee_TG"
        el = "el"
        el_CY = "el_CY"
        el_GR = "el_GR"
        en = "en"
        en_150 = "en_150"
        en_AG = "en_AG"
        en_AS = "en_AS"
        en_AU = "en_AU"
        en_BB = "en_BB"
        en_BE = "en_BE"
        en_BM = "en_BM"
        en_BS = "en_BS"
        en_BW = "en_BW"
        en_BZ = "en_BZ"
        en_CA = "en_CA"
        en_CM = "en_CM"
        en_DM = "en_DM"
        en_FJ = "en_FJ"
        en_FM = "en_FM"
        en_GB = "en_GB"
        en_GD = "en_GD"
        en_GG = "en_GG"
        en_GH = "en_GH"
        en_GI = "en_GI"
        en_GM = "en_GM"
        en_GU = "en_GU"
        en_GY = "en_GY"
        en_HK = "en_HK"
        en_IE = "en_IE"
        en_IM = "en_IM"
        en_IN = "en_IN"
        en_JE = "en_JE"
        en_JM = "en_JM"
        en_KE = "en_KE"
        en_KI = "en_KI"
        en_KN = "en_KN"
        en_KY = "en_KY"
        en_LC = "en_LC"
        en_LR = "en_LR"
        en_LS = "en_LS"
        en_MG = "en_MG"
        en_MH = "en_MH"
        en_MP = "en_MP"
        en_MT = "en_MT"
        en_MU = "en_MU"
        en_MW = "en_MW"
        en_NA = "en_NA"
        en_NG = "en_NG"
        en_NZ = "en_NZ"
        en_PG = "en_PG"
        en_PH = "en_PH"
        en_PK = "en_PK"
        en_PR = "en_PR"
        en_PW = "en_PW"
        en_SB = "en_SB"
        en_SC = "en_SC"
        en_SG = "en_SG"
        en_SL = "en_SL"
        en_SS = "en_SS"
        en_SZ = "en_SZ"
        en_TC = "en_TC"
        en_TO = "en_TO"
        en_TT = "en_TT"
        en_TZ = "en_TZ"
        en_UG = "en_UG"
        en_UM = "en_UM"
        en_US = "en_US"
        en_US_POSIX = "en_US_POSIX"
        en_VC = "en_VC"
        en_VG = "en_VG"
        en_VI = "en_VI"
        en_VU = "en_VU"
        en_WS = "en_WS"
        en_ZA = "en_ZA"
        en_ZM = "en_ZM"
        en_ZW = "en_ZW"
        eo = "eo"
        es = "es"
        es_419 = "es_419"
        es_AR = "es_AR"
        es_BO = "es_BO"
        es_CL = "es_CL"
        es_CO = "es_CO"
        es_CR = "es_CR"
        es_CU = "es_CU"
        es_DO = "es_DO"
        es_EA = "es_EA"
        es_EC = "es_EC"
        es_ES = "es_ES"
        es_GQ = "es_GQ"
        es_GT = "es_GT"
        es_HN = "es_HN"
        es_IC = "es_IC"
        es_MX = "es_MX"
        es_NI = "es_NI"
        es_PA = "es_PA"
        es_PE = "es_PE"
        es_PH = "es_PH"
        es_PR = "es_PR"
        es_PY = "es_PY"
        es_SV = "es_SV"
        es_US = "es_US"
        es_UY = "es_UY"
        es_VE = "es_VE"
        et = "et"
        et_EE = "et_EE"
        eu = "eu"
        eu_ES = "eu_ES"
        ewo = "ewo"
        ewo_CM = "ewo_CM"
        fa = "fa"
        fa_AF = "fa_AF"
        fa_IR = "fa_IR"
        ff = "ff"
        ff_SN = "ff_SN"
        fi = "fi"
        fi_FI = "fi_FI"
        fil = "fil"
        fil_PH = "fil_PH"
        fo = "fo"
        fo_FO = "fo_FO"
        fr = "fr"
        fr_BE = "fr_BE"
        fr_BF = "fr_BF"
        fr_BI = "fr_BI"
        fr_BJ = "fr_BJ"
        fr_BL = "fr_BL"
        fr_CA = "fr_CA"
        fr_CD = "fr_CD"
        fr_CF = "fr_CF"
        fr_CG = "fr_CG"
        fr_CH = "fr_CH"
        fr_CI = "fr_CI"
        fr_CM = "fr_CM"
        fr_DJ = "fr_DJ"
        fr_DZ = "fr_DZ"
        fr_FR = "fr_FR"
        fr_GA = "fr_GA"
        fr_GF = "fr_GF"
        fr_GN = "fr_GN"
        fr_GP = "fr_GP"
        fr_GQ = "fr_GQ"
        fr_HT = "fr_HT"
        fr_KM = "fr_KM"
        fr_LU = "fr_LU"
        fr_MA = "fr_MA"
        fr_MC = "fr_MC"
        fr_MF = "fr_MF"
        fr_MG = "fr_MG"
        fr_ML = "fr_ML"
        fr_MQ = "fr_MQ"
        fr_MR = "fr_MR"
        fr_MU = "fr_MU"
        fr_NC = "fr_NC"
        fr_NE = "fr_NE"
        fr_PF = "fr_PF"
        fr_RE = "fr_RE"
        fr_RW = "fr_RW"
        fr_SC = "fr_SC"
        fr_SN = "fr_SN"
        fr_SY = "fr_SY"
        fr_TD = "fr_TD"
        fr_TG = "fr_TG"
        fr_TN = "fr_TN"
        fr_VU = "fr_VU"
        fr_YT = "fr_YT"
        ga = "ga"
        ga_IE = "ga_IE"
        gl = "gl"
        gl_ES = "gl_ES"
        gsw = "gsw"
        gsw_CH = "gsw_CH"
        gu = "gu"
        gu_IN = "gu_IN"
        guz = "guz"
        guz_KE = "guz_KE"
        gv = "gv"
        gv_GB = "gv_GB"
        ha = "ha"
        ha_Latn = "ha_Latn"
        ha_Latn_GH = "ha_Latn_GH"
        ha_Latn_NE = "ha_Latn_NE"
        ha_Latn_NG = "ha_Latn_NG"
        haw = "haw"
        haw_US = "haw_US"
        he = "he"
        he_IL = "he_IL"
        hi = "hi"
        hi_IN = "hi_IN"
        hr = "hr"
        hr_BA = "hr_BA"
        hr_HR = "hr_HR"
        hu = "hu"
        hu_HU = "hu_HU"
        hy = "hy"
        hy_AM = "hy_AM"
        id = "id"
        id_ID = "id_ID"
        ig = "ig"
        ig_NG = "ig_NG"
        ii = "ii"
        ii_CN = "ii_CN"
        is_ = "is"
        is_IS = "is_IS"
        it = "it"
        it_CH = "it_CH"
        it_IT = "it_IT"
        it_SM = "it_SM"
        ja = "ja"
        ja_JP = "ja_JP"
        jgo = "jgo"
        jgo_CM = "jgo_CM"
        jmc = "jmc"
        jmc_TZ = "jmc_TZ"
        ka = "ka"
        ka_GE = "ka_GE"
        kab = "kab"
        kab_DZ = "kab_DZ"
        kam = "kam"
        kam_KE = "kam_KE"
        kde = "kde"
        kde_TZ = "kde_TZ"
        kea = "kea"
        kea_CV = "kea_CV"
        khq = "khq"
        khq_ML = "khq_ML"
        ki = "ki"
        ki_KE = "ki_KE"
        kk = "kk"
        kk_Cyrl = "kk_Cyrl"
        kk_Cyrl_KZ = "kk_Cyrl_KZ"
        kl = "kl"
        kl_GL = "kl_GL"
        kln = "kln"
        kln_KE = "kln_KE"
        km = "km"
        km_KH = "km_KH"
        kn = "kn"
        kn_IN = "kn_IN"
        ko = "ko"
        ko_KP = "ko_KP"
        ko_KR = "ko_KR"
        kok = "kok"
        kok_IN = "kok_IN"
        ks = "ks"
        ks_Arab = "ks_Arab"
        ks_Arab_IN = "ks_Arab_IN"
        ksb = "ksb"
        ksb_TZ = "ksb_TZ"
        ksf = "ksf"
        ksf_CM = "ksf_CM"
        kw = "kw"
        kw_GB = "kw_GB"
        lag = "lag"
        lag_TZ = "lag_TZ"
        lg = "lg"
        lg_UG = "lg_UG"
        ln = "ln"
        ln_AO = "ln_AO"
        ln_CD = "ln_CD"
        ln_CF = "ln_CF"
        ln_CG = "ln_CG"
        lo = "lo"
        lo_LA = "lo_LA"
        lt = "lt"
        lt_LT = "lt_LT"
        lu = "lu"
        lu_CD = "lu_CD"
        luo = "luo"
        luo_KE = "luo_KE"
        luy = "luy"
        luy_KE = "luy_KE"
        lv = "lv"
        lv_LV = "lv_LV"
        mas = "mas"
        mas_KE = "mas_KE"
        mas_TZ = "mas_TZ"
        mer = "mer"
        mer_KE = "mer_KE"
        mfe = "mfe"
        mfe_MU = "mfe_MU"
        mg = "mg"
        mg_MG = "mg_MG"
        mgh = "mgh"
        mgh_MZ = "mgh_MZ"
        mgo = "mgo"
        mgo_CM = "mgo_CM"
        mk = "mk"
        mk_MK = "mk_MK"
        ml = "ml"
        ml_IN = "ml_IN"
        mr = "mr"
        mr_IN = "mr_IN"
        ms = "ms"
        ms_BN = "ms_BN"
        ms_MY = "ms_MY"
        ms_SG = "ms_SG"
        mt = "mt"
        mt_MT = "mt_MT"
        mua = "mua"
        mua_CM = "mua_CM"
        my = "my"
        my_MM = "my_MM"
        naq = "naq"
        naq_NA = "naq_NA"
        nb = "nb"
        nb_NO = "nb_NO"
        nd = "nd"
        nd_ZW = "nd_ZW"
        ne = "ne"
        ne_IN = "ne_IN"
        ne_NP = "ne_NP"
        nl = "nl"
        nl_AW = "nl_AW"
        nl_BE = "nl_BE"
        nl_CW = "nl_CW"
        nl_NL = "nl_NL"
        nl_SR = "nl_SR"
        nl_SX = "nl_SX"
        nmg = "nmg"
        nmg_CM = "nmg_CM"
        nn = "nn"
        nn_NO = "nn_NO"
        nus = "nus"
        nus_SD = "nus_SD"
        nyn = "nyn"
        nyn_UG = "nyn_UG"
        om = "om"
        om_ET = "om_ET"
        om_KE = "om_KE"
        or_ = "or"
        or_IN = "or_IN"
        pa = "pa"
        pa_Arab = "pa_Arab"
        pa_Arab_PK = "pa_Arab_PK"
        pa_Guru = "pa_Guru"
        pa_Guru_IN = "pa_Guru_IN"
        pl = "pl"
        pl_PL = "pl_PL"
        ps = "ps"
        ps_AF = "ps_AF"
        pt = "pt"
        pt_AO = "pt_AO"
        pt_BR = "pt_BR"
        pt_CV = "pt_CV"
        pt_GW = "pt_GW"
        pt_MO = "pt_MO"
        pt_MZ = "pt_MZ"
        pt_PT = "pt_PT"
        pt_ST = "pt_ST"
        pt_TL = "pt_TL"
        rm = "rm"
        rm_CH = "rm_CH"
        rn = "rn"
        rn_BI = "rn_BI"
        ro = "ro"
        ro_MD = "ro_MD"
        ro_RO = "ro_RO"
        rof = "rof"
        rof_TZ = "rof_TZ"
        ru = "ru"
        ru_BY = "ru_BY"
        ru_KG = "ru_KG"
        ru_KZ = "ru_KZ"
        ru_MD = "ru_MD"
        ru_RU = "ru_RU"
        ru_UA = "ru_UA"
        rw = "rw"
        rw_RW = "rw_RW"
        rwk = "rwk"
        rwk_TZ = "rwk_TZ"
        saq = "saq"
        saq_KE = "saq_KE"
        sbp = "sbp"
        sbp_TZ = "sbp_TZ"
        seh = "seh"
        seh_MZ = "seh_MZ"
        ses = "ses"
        ses_ML = "ses_ML"
        sg = "sg"
        sg_CF = "sg_CF"
        shi = "shi"
        shi_Latn = "shi_Latn"
        shi_Latn_MA = "shi_Latn_MA"
        shi_Tfng = "shi_Tfng"
        shi_Tfng_MA = "shi_Tfng_MA"
        si = "si"
        si_LK = "si_LK"
        sk = "sk"
        sk_SK = "sk_SK"
        sl = "sl"
        sl_SI = "sl_SI"
        sn = "sn"
        sn_ZW = "sn_ZW"
        so = "so"
        so_DJ = "so_DJ"
        so_ET = "so_ET"
        so_KE = "so_KE"
        so_SO = "so_SO"
        sq = "sq"
        sq_AL = "sq_AL"
        sq_MK = "sq_MK"
        sr = "sr"
        sr_Cyrl = "sr_Cyrl"
        sr_Cyrl_BA = "sr_Cyrl_BA"
        sr_Cyrl_ME = "sr_Cyrl_ME"
        sr_Cyrl_RS = "sr_Cyrl_RS"
        sr_Latn = "sr_Latn"
        sr_Latn_BA = "sr_Latn_BA"
        sr_Latn_ME = "sr_Latn_ME"
        sr_Latn_RS = "sr_Latn_RS"
        sv = "sv"
        sv_AX = "sv_AX"
        sv_FI = "sv_FI"
        sv_SE = "sv_SE"
        sw = "sw"
        sw_KE = "sw_KE"
        sw_TZ = "sw_TZ"
        sw_UG = "sw_UG"
        swc = "swc"
        swc_CD = "swc_CD"
        ta = "ta"
        ta_IN = "ta_IN"
        ta_LK = "ta_LK"
        ta_MY = "ta_MY"
        ta_SG = "ta_SG"
        te = "te"
        te_IN = "te_IN"
        teo = "teo"
        teo_KE = "teo_KE"
        teo_UG = "teo_UG"
        th = "th"
        th_TH = "th_TH"
        ti = "ti"
        ti_ER = "ti_ER"
        ti_ET = "ti_ET"
        to = "to"
        to_TO = "to_TO"
        tr = "tr"
        tr_CY = "tr_CY"
        tr_TR = "tr_TR"
        twq = "twq"
        twq_NE = "twq_NE"
        tzm = "tzm"
        tzm_Latn = "tzm_Latn"
        tzm_Latn_MA = "tzm_Latn_MA"
        uk = "uk"
        uk_UA = "uk_UA"
        ur = "ur"
        ur_IN = "ur_IN"
        ur_PK = "ur_PK"
        uz = "uz"
        uz_Arab = "uz_Arab"
        uz_Arab_AF = "uz_Arab_AF"
        uz_Cyrl = "uz_Cyrl"
        uz_Cyrl_UZ = "uz_Cyrl_UZ"
        uz_Latn = "uz_Latn"
        uz_Latn_UZ = "uz_Latn_UZ"
        vai = "vai"
        vai_Latn = "vai_Latn"
        vai_Latn_LR = "vai_Latn_LR"
        vai_Vaii = "vai_Vaii"
        vai_Vaii_LR = "vai_Vaii_LR"
        vi = "vi"
        vi_VN = "vi_VN"
        vun = "vun"
        vun_TZ = "vun_TZ"
        xog = "xog"
        xog_UG = "xog_UG"
        yav = "yav"
        yav_CM = "yav_CM"
        yo = "yo"
        yo_NG = "yo_NG"
        zh = "zh"
        zh_Hans = "zh_Hans"
        zh_Hans_CN = "zh_Hans_CN"
        zh_Hans_HK = "zh_Hans_HK"
        zh_Hans_MO = "zh_Hans_MO"
        zh_Hans_SG = "zh_Hans_SG"
        zh_Hant = "zh_Hant"
        zh_Hant_HK = "zh_Hant_HK"
        zh_Hant_MO = "zh_Hant_MO"
        zh_Hant_TW = "zh_Hant_TW"
        zu = "zu"
        zu_ZA = "zu_ZA"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class SEQUENTIALFILE:
    """Enums for properties in the SEQUENTIALFILE stage."""

    class AppendOverwrite(Enum):
        """Enum for the AppendOverwrite property."""

        overwrite = "overwrite"
        append = "append"
        create = " "

    class CleanupOnFailure(Enum):
        """Enum for the CleanupOnFailure property."""

        false = " "
        true = "nocleanup"

    class RejectMode(Enum):
        """Enum for the RejectMode property."""

        save = "save"
        cont = "continue"
        fail = "fail"

    class FirstLineColumnNames(Enum):
        """Enum for the FirstLineColumnNames property."""

        true = "firstLineColumnNames"
        false = " "

    class WriteMethod(Enum):
        """Enum for the WriteMethod property."""

        multiple = "filepattern"
        specific = " "

    class ForceSequential(Enum):
        """Enum for the ForceSequential property."""

        true = "sequential"
        false = " "

    class ExcludePart(Enum):
        """Enum for the ExcludePart property."""

        true = "excludePart"
        false = " "

    class UseValueInFilename(Enum):
        """Enum for the UseValueInFilename property."""

        true = "include"
        false = " "

    class CiCs(Enum):
        """Enum for the CiCs property."""

        cs = "cs"
        ci = "ci"

    class AscDesc(Enum):
        """Enum for the AscDesc property."""

        desc = "desc"
        asc = "asc"

    class NullsPosition(Enum):
        """Enum for the NullsPosition property."""

        last = "last"
        first = "first"

    class SortAsEbcdic(Enum):
        """Enum for the SortAsEbcdic property."""

        true = "ebcdic"
        false = " "

    class FileLocation(Enum):
        """Enum for the FileLocation property."""

        file_system = "file_system"
        connection = "connection"

    class FileFormat(Enum):
        """Enum for the FileFormat property."""

        sequential = "sequential"
        parquet = "parquet"

    class CompressionCodec(Enum):
        """Enum for the CompressionCodec property."""

        none = "none"
        snappy = "snappy"
        gzip = "gzip"
        lzo = "lzo"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        file = "file"
        pattern = "pattern"

    class KeepPartitions(Enum):
        """Enum for the KeepPartitions property."""

        true = "keepPartitions"
        false = " "

    class MissingFile(Enum):
        """Enum for the MissingFile property."""

        error = "error"
        custom = " "
        okay = "okay"

    class ReportProgress(Enum):
        """Enum for the ReportProgress property."""

        no = "no"
        yes = "yes"

    class ReadFromMultipleNodes(Enum):
        """Enum for the ReadFromMultipleNodes property."""

        no = " "
        yes = "yes"

    class StripBom(Enum):
        """Enum for the StripBom property."""

        true = "stripbom"
        false = " "

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_seq = "default_seq"
        default_par = "default_par"
        seq = "seq"
        par = "par"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_set = -2
        default_clear = -1
        clear = 0
        set = 1

    class MapName(Enum):
        """Enum for the MapName property."""

        Adobe_Standard_Encoding = "Adobe-Standard-Encoding"
        ANSI_X3_4_1968 = "ANSI_X3.4-1968"
        ASCL_ASCII = "ASCL_ASCII"
        ASCL_ASCII_PC1 = "ASCL_ASCII-PC1"
        ASCL_BIG5 = "ASCL_BIG5"
        ASCL_C0_CONTROLS = "ASCL_C0-CONTROLS"
        ASCL_C1_CONTROLS = "ASCL_C1-CONTROLS"
        ASCL_EBCDIC = "ASCL_EBCDIC"
        ASCL_EBCDIC_037 = "ASCL_EBCDIC-037"
        ASCL_EBCDIC_1026 = "ASCL_EBCDIC-1026"
        ASCL_EBCDIC_500V1 = "ASCL_EBCDIC-500V1"
        ASCL_EBCDIC_875 = "ASCL_EBCDIC-875"
        ASCL_EBCDIC_CTRLS = "ASCL_EBCDIC-CTRLS"
        ASCL_EBCDIC_IBM1364 = "ASCL_EBCDIC-IBM1364"
        ASCL_EBCDIC_IBM1371 = "ASCL_EBCDIC-IBM1371"
        ASCL_EBCDIC_IBM933 = "ASCL_EBCDIC-IBM933"
        ASCL_EBCDIC_IBM937 = "ASCL_EBCDIC-IBM937"
        ASCL_EBCDIC_JP_CTRLS = "ASCL_EBCDIC-JP-CTRLS"
        ASCL_EBCDIC_JP_KANA = "ASCL_EBCDIC-JP-KANA"
        ASCL_EBCDIC_JP_KANA_E = "ASCL_EBCDIC-JP-KANA-E"
        ASCL_EBCDIC_JP_KANA_HW = "ASCL_EBCDIC-JP-KANA-HW"
        ASCL_GB2312 = "ASCL_GB2312"
        ASCL_ISO8859_1 = "ASCL_ISO8859-1"
        ASCL_ISO8859_10 = "ASCL_ISO8859-10"
        ASCL_ISO8859_15 = "ASCL_ISO8859-15"
        ASCL_ISO8859_2 = "ASCL_ISO8859-2"
        ASCL_ISO8859_3 = "ASCL_ISO8859-3"
        ASCL_ISO8859_4 = "ASCL_ISO8859-4"
        ASCL_ISO8859_5 = "ASCL_ISO8859-5"
        ASCL_ISO8859_6 = "ASCL_ISO8859-6"
        ASCL_ISO8859_7 = "ASCL_ISO8859-7"
        ASCL_ISO8859_8 = "ASCL_ISO8859-8"
        ASCL_ISO8859_9 = "ASCL_ISO8859-9"
        ASCL_JIS_EUC = "ASCL_JIS-EUC"
        ASCL_JIS_EUC_HWK = "ASCL_JIS-EUC-HWK"
        ASCL_JIS_EUC_P = "ASCL_JIS-EUC-P"
        ASCL_JIS_ROMAN = "ASCL_JIS-ROMAN"
        ASCL_JISX0201 = "ASCL_JISX0201"
        ASCL_JPN_EBCDIC = "ASCL_JPN-EBCDIC"
        ASCL_JPN_EBCDIK = "ASCL_JPN-EBCDIK"
        ASCL_JPN_EBCDIKC_CTRL = "ASCL_JPN-EBCDIKC-CTRL"
        ASCL_JPN_EUC = "ASCL_JPN-EUC"
        ASCL_JPN_EUC_KAT = "ASCL_JPN-EUC-KAT"
        ASCL_JPN_EUC_ONE = "ASCL_JPN-EUC-ONE"
        ASCL_JPN_EUC_RTE = "ASCL_JPN-EUC-RTE"
        ASCL_JPN_EUC_TWO = "ASCL_JPN-EUC-TWO"
        ASCL_JPN_IBM78 = "ASCL_JPN-IBM78"
        ASCL_JPN_IBM83 = "ASCL_JPN-IBM83"
        ASCL_JPN_JEF78 = "ASCL_JPN-JEF78"
        ASCL_JPN_JEF83 = "ASCL_JPN-JEF83"
        ASCL_JPN_JIPSE = "ASCL_JPN-JIPSE"
        ASCL_JPN_JIPSJ = "ASCL_JPN-JIPSJ"
        ASCL_JPN_JIS_RTE = "ASCL_JPN-JIS-RTE"
        ASCL_JPN_JIS8 = "ASCL_JPN-JIS8"
        ASCL_JPN_JIS8EUC_CTRL = "ASCL_JPN-JIS8EUC-CTRL"
        ASCL_JPN_KEIS_RTE = "ASCL_JPN-KEIS-RTE"
        ASCL_JPN_KEIS78 = "ASCL_JPN-KEIS78"
        ASCL_JPN_KEIS83 = "ASCL_JPN-KEIS83"
        ASCL_JPN_NEBCDIK = "ASCL_JPN-NEBCDIK"
        ASCL_JPN_SJIS = "ASCL_JPN-SJIS"
        ASCL_KOI8_R = "ASCL_KOI8-R"
        ASCL_KSC5601 = "ASCL_KSC5601"
        ASCL_KSC5601_1992 = "ASCL_KSC5601-1992"
        ASCL_MAC_GREEK = "ASCL_MAC-GREEK"
        ASCL_MAC_GREEK2 = "ASCL_MAC-GREEK2"
        ASCL_MAC_ROMAN = "ASCL_MAC-ROMAN"
        ASCL_MNEMONICS = "ASCL_MNEMONICS"
        ASCL_MS1250 = "ASCL_MS1250"
        ASCL_MS1251 = "ASCL_MS1251"
        ASCL_MS1252 = "ASCL_MS1252"
        ASCL_MS1253 = "ASCL_MS1253"
        ASCL_MS1254 = "ASCL_MS1254"
        ASCL_MS1255 = "ASCL_MS1255"
        ASCL_MS1256 = "ASCL_MS1256"
        ASCL_MS932 = "ASCL_MS932"
        ASCL_MS932_BASE = "ASCL_MS932-BASE"
        ASCL_MS932_EXTRA = "ASCL_MS932-EXTRA"
        ASCL_MS936 = "ASCL_MS936"
        ASCL_MS936_BASE = "ASCL_MS936-BASE"
        ASCL_MS949 = "ASCL_MS949"
        ASCL_MS950 = "ASCL_MS950"
        ASCL_MS950_BASE = "ASCL_MS950-BASE"
        ASCL_PC1040 = "ASCL_PC1040"
        ASCL_PC1041 = "ASCL_PC1041"
        ASCL_PC437 = "ASCL_PC437"
        ASCL_PC850 = "ASCL_PC850"
        ASCL_PC852 = "ASCL_PC852"
        ASCL_PC855 = "ASCL_PC855"
        ASCL_PC857 = "ASCL_PC857"
        ASCL_PC860 = "ASCL_PC860"
        ASCL_PC861 = "ASCL_PC861"
        ASCL_PC862 = "ASCL_PC862"
        ASCL_PC863 = "ASCL_PC863"
        ASCL_PC864 = "ASCL_PC864"
        ASCL_PC865 = "ASCL_PC865"
        ASCL_PC866 = "ASCL_PC866"
        ASCL_PC869 = "ASCL_PC869"
        ASCL_PC874 = "ASCL_PC874"
        ASCL_PRIME_SHIFT_JIS = "ASCL_PRIME-SHIFT-JIS"
        ASCL_SHIFT_JIS = "ASCL_SHIFT-JIS"
        ASCL_TAU_SHIFT_JIS = "ASCL_TAU-SHIFT-JIS"
        ASCL_TIS620 = "ASCL_TIS620"
        ASCL_TIS620_B = "ASCL_TIS620-B"
        Big5 = "Big5"
        Big5_HKSCS = "Big5-HKSCS"
        BOCU_1 = "BOCU-1"
        CESU_8 = "CESU-8"
        ebcdic_xml_us = "ebcdic-xml-us"
        EUC_KR = "EUC-KR"
        GB_2312_80 = "GB_2312-80"
        gb18030_gb18030 = "gb18030 gb18030"
        GB2312 = "GB2312"
        GBK = "GBK"
        hp_roman8 = "hp-roman8"
        HZ_HZ_GB_2312 = "HZ HZ-GB-2312"
        ibm_1006_P100_1995 = "ibm-1006_P100-1995"
        ibm_1025_P100_1995 = "ibm-1025_P100-1995"
        ibm_1026_P100_1995 = "ibm-1026_P100-1995"
        ibm_1047_P100_1995 = "ibm-1047_P100-1995"
        ibm_1047_P100_1995_swaplfnl = "ibm-1047_P100-1995,swaplfnl"
        ibm_1051_P100_1995 = "ibm-1051_P100-1995"
        ibm_1089_P100_1995 = "ibm-1089_P100-1995"
        ibm_1097_P100_1995 = "ibm-1097_P100-1995"
        ibm_1098_P100_1995 = "ibm-1098_P100-1995"
        ibm_1112_P100_1995 = "ibm-1112_P100-1995"
        ibm_1122_P100_1999 = "ibm-1122_P100-1999"
        ibm_1123_P100_1995 = "ibm-1123_P100-1995"
        ibm_1124_P100_1996 = "ibm-1124_P100-1996"
        ibm_1125_P100_1997 = "ibm-1125_P100-1997"
        ibm_1129_P100_1997 = "ibm-1129_P100-1997"
        ibm_1130_P100_1997 = "ibm-1130_P100-1997"
        ibm_1131_P100_1997 = "ibm-1131_P100-1997"
        ibm_1132_P100_1998 = "ibm-1132_P100-1998"
        ibm_1133_P100_1997 = "ibm-1133_P100-1997"
        ibm_1137_P100_1999 = "ibm-1137_P100-1999"
        ibm_1140_P100_1997 = "ibm-1140_P100-1997"
        ibm_1140_P100_1997_swaplfnl = "ibm-1140_P100-1997,swaplfnl"
        ibm_1141_P100_1997 = "ibm-1141_P100-1997"
        ibm_1141_P100_1997_swaplfnl = "ibm-1141_P100-1997,swaplfnl"
        ibm_1142_P100_1997 = "ibm-1142_P100-1997"
        ibm_1142_P100_1997_swaplfnl = "ibm-1142_P100-1997,swaplfnl"
        ibm_1143_P100_1997 = "ibm-1143_P100-1997"
        ibm_1143_P100_1997_swaplfnl = "ibm-1143_P100-1997,swaplfnl"
        ibm_1144_P100_1997 = "ibm-1144_P100-1997"
        ibm_1144_P100_1997_swaplfnl = "ibm-1144_P100-1997,swaplfnl"
        ibm_1145_P100_1997 = "ibm-1145_P100-1997"
        ibm_1145_P100_1997_swaplfnl = "ibm-1145_P100-1997,swaplfnl"
        ibm_1146_P100_1997 = "ibm-1146_P100-1997"
        ibm_1146_P100_1997_swaplfnl = "ibm-1146_P100-1997,swaplfnl"
        ibm_1147_P100_1997 = "ibm-1147_P100-1997"
        ibm_1147_P100_1997_swaplfnl = "ibm-1147_P100-1997,swaplfnl"
        ibm_1148_P100_1997 = "ibm-1148_P100-1997"
        ibm_1148_P100_1997_swaplfnl = "ibm-1148_P100-1997,swaplfnl"
        ibm_1149_P100_1997 = "ibm-1149_P100-1997"
        ibm_1149_P100_1997_swaplfnl = "ibm-1149_P100-1997,swaplfnl"
        ibm_1153_P100_1999 = "ibm-1153_P100-1999"
        ibm_1153_P100_1999_swaplfnl = "ibm-1153_P100-1999,swaplfnl"
        ibm_1154_P100_1999 = "ibm-1154_P100-1999"
        ibm_1155_P100_1999 = "ibm-1155_P100-1999"
        ibm_1156_P100_1999 = "ibm-1156_P100-1999"
        ibm_1157_P100_1999 = "ibm-1157_P100-1999"
        ibm_1158_P100_1999 = "ibm-1158_P100-1999"
        ibm_1160_P100_1999 = "ibm-1160_P100-1999"
        ibm_1162_P100_1999 = "ibm-1162_P100-1999"
        ibm_1164_P100_1999 = "ibm-1164_P100-1999"
        ibm_1168_P100_2002 = "ibm-1168_P100-2002"
        ibm_1250_P100_1995 = "ibm-1250_P100-1995"
        ibm_1251_P100_1995 = "ibm-1251_P100-1995"
        ibm_1252_P100_2000 = "ibm-1252_P100-2000"
        ibm_1253_P100_1995 = "ibm-1253_P100-1995"
        ibm_1254_P100_1995 = "ibm-1254_P100-1995"
        ibm_1255_P100_1995 = "ibm-1255_P100-1995"
        ibm_1256_P110_1997 = "ibm-1256_P110-1997"
        ibm_1257_P100_1995 = "ibm-1257_P100-1995"
        ibm_1258_P100_1997 = "ibm-1258_P100-1997"
        ibm_12712_P100_1998 = "ibm-12712_P100-1998"
        ibm_12712_P100_1998_swaplfnl = "ibm-12712_P100-1998,swaplfnl"
        ibm_1276_P100_1995 = "ibm-1276_P100-1995"
        ibm_1277_P100_1995 = "ibm-1277_P100-1995"
        ibm_1363_P110_1997 = "ibm-1363_P110-1997"
        ibm_1363_P11B_1998 = "ibm-1363_P11B-1998"
        ibm_1364_P110_1997 = "ibm-1364_P110-1997"
        ibm_1364_P110_2007 = "ibm-1364_P110-2007"
        ibm_1371_P100_1999 = "ibm-1371_P100-1999"
        ibm_1373_P100_2002 = "ibm-1373_P100-2002"
        ibm_1375_P100_2003 = "ibm-1375_P100-2003"
        ibm_1375_P100_2007 = "ibm-1375_P100-2007"
        ibm_1381_P110_1999 = "ibm-1381_P110-1999"
        ibm_1383_P110_1999 = "ibm-1383_P110-1999"
        ibm_1386_P100_2001 = "ibm-1386_P100-2001"
        ibm_1386_P100_2002 = "ibm-1386_P100-2002"
        ibm_1388_P103_2001 = "ibm-1388_P103-2001"
        ibm_1390_P110_2003 = "ibm-1390_P110-2003"
        ibm_1399_P110_2003 = "ibm-1399_P110-2003"
        ibm_16684_P110_2003 = "ibm-16684_P110-2003"
        ibm_16804_X110_1999 = "ibm-16804_X110-1999"
        ibm_16804_X110_1999_swaplfnl = "ibm-16804_X110-1999,swaplfnl"
        ibm_273_P100_1995 = "ibm-273_P100-1995"
        ibm_277_P100_1995 = "ibm-277_P100-1995"
        ibm_278_P100_1995 = "ibm-278_P100-1995"
        ibm_280_P100_1995 = "ibm-280_P100-1995"
        ibm_284_P100_1995 = "ibm-284_P100-1995"
        ibm_285_P100_1995 = "ibm-285_P100-1995"
        ibm_290_P100_1995 = "ibm-290_P100-1995"
        ibm_297_P100_1995 = "ibm-297_P100-1995"
        ibm_33722_P120_1999 = "ibm-33722_P120-1999"
        ibm_33722_P12A_P12A_2009_U2_Extended_UNIX_Code_Packed_Format_for_Japanese = (
            "ibm-33722_P12A_P12A-2009_U2 Extended_UNIX_Code_Packed_Format_for_Japanese"
        )
        ibm_33722_P12A_1999 = "ibm-33722_P12A-1999"
        ibm_367_P100_1995 = "ibm-367_P100-1995"
        ibm_37_P100_1995 = "ibm-37_P100-1995"
        ibm_37_P100_1995_swaplfnl = "ibm-37_P100-1995,swaplfnl"
        ibm_420_X120_1999 = "ibm-420_X120-1999"
        ibm_424_P100_1995 = "ibm-424_P100-1995"
        ibm_437_P100_1995 = "ibm-437_P100-1995"
        ibm_4517_P100_2005 = "ibm-4517_P100-2005"
        ibm_4899_P100_1998 = "ibm-4899_P100-1998"
        ibm_4909_P100_1999 = "ibm-4909_P100-1999"
        ibm_4971_P100_1999 = "ibm-4971_P100-1999"
        ibm_500_P100_1995 = "ibm-500_P100-1995"
        ibm_5012_P100_1999 = "ibm-5012_P100-1999"
        ibm_5123_P100_1999 = "ibm-5123_P100-1999"
        ibm_5346_P100_1998 = "ibm-5346_P100-1998"
        ibm_5347_P100_1998 = "ibm-5347_P100-1998"
        ibm_5348_P100_1997 = "ibm-5348_P100-1997"
        ibm_5349_P100_1998 = "ibm-5349_P100-1998"
        ibm_5350_P100_1998 = "ibm-5350_P100-1998"
        ibm_5351_P100_1998 = "ibm-5351_P100-1998"
        ibm_5352_P100_1998 = "ibm-5352_P100-1998"
        ibm_5353_P100_1998 = "ibm-5353_P100-1998"
        ibm_5354_P100_1998 = "ibm-5354_P100-1998"
        ibm_5471_P100_2006 = "ibm-5471_P100-2006"
        ibm_5478_P100_1995 = "ibm-5478_P100-1995"
        ibm_720_P100_1997 = "ibm-720_P100-1997"
        ibm_737_P100_1997 = "ibm-737_P100-1997"
        ibm_775_P100_1996 = "ibm-775_P100-1996"
        ibm_803_P100_1999 = "ibm-803_P100-1999"
        ibm_813_P100_1995 = "ibm-813_P100-1995"
        ibm_838_P100_1995 = "ibm-838_P100-1995"
        ibm_8482_P100_1999 = "ibm-8482_P100-1999"
        ibm_850_P100_1995 = "ibm-850_P100-1995"
        ibm_851_P100_1995 = "ibm-851_P100-1995"
        ibm_852_P100_1995 = "ibm-852_P100-1995"
        ibm_855_P100_1995 = "ibm-855_P100-1995"
        ibm_856_P100_1995 = "ibm-856_P100-1995"
        ibm_857_P100_1995 = "ibm-857_P100-1995"
        ibm_858_P100_1997 = "ibm-858_P100-1997"
        ibm_860_P100_1995 = "ibm-860_P100-1995"
        ibm_861_P100_1995 = "ibm-861_P100-1995"
        ibm_862_P100_1995 = "ibm-862_P100-1995"
        ibm_863_P100_1995 = "ibm-863_P100-1995"
        ibm_864_X110_1999 = "ibm-864_X110-1999"
        ibm_865_P100_1995 = "ibm-865_P100-1995"
        ibm_866_P100_1995 = "ibm-866_P100-1995"
        ibm_867_P100_1998 = "ibm-867_P100-1998"
        ibm_868_P100_1995 = "ibm-868_P100-1995"
        ibm_869_P100_1995 = "ibm-869_P100-1995"
        ibm_870_P100_1995 = "ibm-870_P100-1995"
        ibm_871_P100_1995 = "ibm-871_P100-1995"
        ibm_874_P100_1995 = "ibm-874_P100-1995"
        ibm_875_P100_1995 = "ibm-875_P100-1995"
        ibm_878_P100_1996 = "ibm-878_P100-1996"
        ibm_897_P100_1995 = "ibm-897_P100-1995"
        ibm_9005_X110_2007 = "ibm-9005_X110-2007"
        ibm_901_P100_1999 = "ibm-901_P100-1999"
        ibm_902_P100_1999 = "ibm-902_P100-1999"
        ibm_9067_X100_2005 = "ibm-9067_X100-2005"
        ibm_912_P100_1995 = "ibm-912_P100-1995"
        ibm_913_P100_2000 = "ibm-913_P100-2000"
        ibm_914_P100_1995 = "ibm-914_P100-1995"
        ibm_915_P100_1995 = "ibm-915_P100-1995"
        ibm_916_P100_1995 = "ibm-916_P100-1995"
        ibm_918_P100_1995 = "ibm-918_P100-1995"
        ibm_920_P100_1995 = "ibm-920_P100-1995"
        ibm_921_P100_1995 = "ibm-921_P100-1995"
        ibm_922_P100_1999 = "ibm-922_P100-1999"
        ibm_923_P100_1998 = "ibm-923_P100-1998"
        ibm_930_P120_1999 = "ibm-930_P120-1999"
        ibm_933_P110_1995 = "ibm-933_P110-1995"
        ibm_935_P110_1999 = "ibm-935_P110-1999"
        ibm_937_P110_1999 = "ibm-937_P110-1999"
        ibm_939_P120_1999 = "ibm-939_P120-1999"
        ibm_942_P12A_1999 = "ibm-942_P12A-1999"
        ibm_943_P130_1999 = "ibm-943_P130-1999"
        ibm_943_P15A_2003 = "ibm-943_P15A-2003"
        ibm_9447_P100_2002 = "ibm-9447_P100-2002"
        ibm_9448_X100_2005 = "ibm-9448_X100-2005"
        ibm_9449_P100_2002 = "ibm-9449_P100-2002"
        ibm_949_P110_1999 = "ibm-949_P110-1999"
        ibm_949_P11A_1999 = "ibm-949_P11A-1999"
        ibm_950_P110_1999 = "ibm-950_P110-1999"
        ibm_954_P101_2000 = "ibm-954_P101-2000"
        ibm_954_P101_2007 = "ibm-954_P101-2007"
        ibm_964_P110_1999 = "ibm-964_P110-1999"
        ibm_970_P110_P110_2006_U2 = "ibm-970_P110_P110-2006_U2"
        ibm_970_P110_1995 = "ibm-970_P110-1995"
        ibm_971_P100_1995 = "ibm-971_P100-1995"
        IBM_Thai = "IBM-Thai"
        IBM00858 = "IBM00858"
        IBM01140 = "IBM01140"
        IBM01141 = "IBM01141"
        IBM01142 = "IBM01142"
        IBM01143 = "IBM01143"
        IBM01144 = "IBM01144"
        IBM01145 = "IBM01145"
        IBM01146 = "IBM01146"
        IBM01147 = "IBM01147"
        IBM01148 = "IBM01148"
        IBM01149 = "IBM01149"
        IBM037 = "IBM037"
        IBM1026 = "IBM1026"
        IBM1047 = "IBM1047"
        IBM273 = "IBM273"
        IBM277 = "IBM277"
        IBM278 = "IBM278"
        IBM280 = "IBM280"
        IBM284 = "IBM284"
        IBM285 = "IBM285"
        IBM290 = "IBM290"
        IBM297 = "IBM297"
        IBM420 = "IBM420"
        IBM424 = "IBM424"
        IBM437 = "IBM437"
        IBM500 = "IBM500"
        IBM775 = "IBM775"
        IBM850 = "IBM850"
        IBM851 = "IBM851"
        IBM852 = "IBM852"
        IBM855 = "IBM855"
        IBM857 = "IBM857"
        IBM860 = "IBM860"
        IBM861 = "IBM861"
        IBM862 = "IBM862"
        IBM863 = "IBM863"
        IBM864 = "IBM864"
        IBM865 = "IBM865"
        IBM866 = "IBM866"
        IBM868 = "IBM868"
        IBM869 = "IBM869"
        IBM870 = "IBM870"
        IBM871 = "IBM871"
        IBM918 = "IBM918"
        IMAP_mailbox_name = "IMAP-mailbox-name"
        ISCII_version_0 = "ISCII,version=0"
        ISCII_version_1 = "ISCII,version=1"
        ISCII_version_2 = "ISCII,version=2"
        ISCII_version_3 = "ISCII,version=3"
        ISCII_version_4 = "ISCII,version=4"
        ISCII_version_5 = "ISCII,version=5"
        ISCII_version_6 = "ISCII,version=6"
        ISCII_version_7 = "ISCII,version=7"
        ISCII_version_8 = "ISCII,version=8"
        ISO_2022_locale_ja_version_0 = "ISO_2022,locale=ja,version=0"
        ISO_2022_locale_ja_version_1 = "ISO_2022,locale=ja,version=1"
        ISO_2022_locale_ja_version_2 = "ISO_2022,locale=ja,version=2"
        ISO_2022_locale_ja_version_3 = "ISO_2022,locale=ja,version=3"
        ISO_2022_locale_ja_version_4 = "ISO_2022,locale=ja,version=4"
        ISO_2022_locale_ko_version_0 = "ISO_2022,locale=ko,version=0"
        ISO_2022_locale_ko_version_1 = "ISO_2022,locale=ko,version=1"
        ISO_2022_locale_zh_version_0 = "ISO_2022,locale=zh,version=0"
        ISO_2022_locale_zh_version_1 = "ISO_2022,locale=zh,version=1"
        ISO_2022_locale_zh_version_2 = "ISO_2022,locale=zh,version=2"
        ISO_8859_1_1987 = "ISO_8859-1:1987"
        ISO_8859_2_1987 = "ISO_8859-2:1987"
        ISO_8859_3_1988 = "ISO_8859-3:1988"
        ISO_8859_4_1988 = "ISO_8859-4:1988"
        ISO_8859_5_1988 = "ISO_8859-5:1988"
        ISO_8859_6_1987 = "ISO_8859-6:1987"
        ISO_8859_7_1987 = "ISO_8859-7:1987"
        ISO_8859_8_1988 = "ISO_8859-8:1988"
        ISO_8859_9_1989 = "ISO_8859-9:1989"
        ISO_2022_CN = "ISO-2022-CN"
        ISO_2022_CN_EXT = "ISO-2022-CN-EXT"
        ISO_2022_JP = "ISO-2022-JP"
        ISO_2022_JP_2 = "ISO-2022-JP-2"
        ISO_2022_KR = "ISO-2022-KR"
        iso_8859_10_1998 = "iso-8859_10-1998"
        iso_8859_11_2001 = "iso-8859_11-2001"
        iso_8859_14_1998 = "iso-8859_14-1998"
        ISO_8859_1 = "ISO-8859-1"
        ISO_8859_10 = "ISO-8859-10"
        ISO_8859_13 = "ISO-8859-13"
        ISO_8859_14 = "ISO-8859-14"
        ISO_8859_15 = "ISO-8859-15"
        JIS_Encoding = "JIS_Encoding"
        KOI8_R = "KOI8-R"
        KOI8_U = "KOI8-U"
        KS_C_5601_1987 = "KS_C_5601-1987"
        LMBCS_1 = "LMBCS-1"
        macintosh = "macintosh"
        macos_0_2_10_2 = "macos-0_2-10.2"
        macos_2566_10_2 = "macos-2566-10.2"
        macos_29_10_2 = "macos-29-10.2"
        macos_35_10_2 = "macos-35-10.2"
        macos_6_2_10_4 = "macos-6_2-10.4"
        macos_6_10_2 = "macos-6-10.2"
        macos_7_3_10_2 = "macos-7_3-10.2"
        SCSU = "SCSU"
        Shift_JIS = "Shift_JIS"
        TIS_620 = "TIS-620"
        US_ASCII = "US-ASCII"
        UTF_16 = "UTF-16"
        UTF_16_version_1 = "UTF-16,version=1"
        UTF_16_version_2 = "UTF-16,version=2"
        UTF_16BE = "UTF-16BE"
        UTF_16BE_version_1 = "UTF-16BE,version=1"
        UTF_16LE = "UTF-16LE"
        UTF_16LE_version_1 = "UTF-16LE,version=1"
        UTF_32 = "UTF-32"
        UTF_32BE = "UTF-32BE"
        UTF_32LE = "UTF-32LE"
        UTF_7 = "UTF-7"
        UTF_8 = "UTF-8"
        UTF16_OppositeEndian = "UTF16_OppositeEndian"
        UTF16_PlatformEndian = "UTF16_PlatformEndian"
        UTF32_OppositeEndian = "UTF32_OppositeEndian"
        UTF32_PlatformEndian = "UTF32_PlatformEndian"
        windows_1250 = "windows-1250"
        windows_1251 = "windows-1251"
        windows_1252 = "windows-1252"
        windows_1253 = "windows-1253"
        windows_1254 = "windows-1254"
        windows_1255 = "windows-1255"
        windows_1256 = "windows-1256"
        windows_1256_2000 = "windows-1256-2000"
        windows_1257 = "windows-1257"
        windows_1258 = "windows-1258"
        windows_874_2000 = "windows-874-2000"
        windows_936_2000 = "windows-936-2000"
        windows_949_2000 = "windows-949-2000"
        windows_950_2000 = "windows-950-2000"
        x11_compound_text = "x11-compound-text"

    class AllowPerColumnMapping(Enum):
        """Enum for the AllowPerColumnMapping property."""

        false = "False"
        true = "True"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class FinalDelimiter(Enum):
        """Enum for the FinalDelimiter property."""

        custom = " "
        ws = "ws"
        end = "end"
        none = "none"
        null = "null"
        comma = "','"
        tab = "'\t'"

    class FillChar(Enum):
        """Enum for the FillChar property."""

        custom_fill_char = -1
        null = 0

    class CheckIntact(Enum):
        """Enum for the CheckIntact property."""

        check_intact = "check_intact"

    class RecordDelimiter(Enum):
        """Enum for the RecordDelimiter property."""

        custom = " "
        newline = "'\n'"
        return_newline = "'\r\n'"
        null = "null"

    class RecordPrefix(Enum):
        """Enum for the RecordPrefix property."""

        one = 1
        two = 2
        four = 4

    class RecordLength(Enum):
        """Enum for the RecordLength property."""

        custom = " "
        fixed = "fixed"

    class RecordType(Enum):
        """Enum for the RecordType property."""

        type_implicit = "{type=implicit}"
        type_varying = "{type=varying}"
        type_varying_format_V = "{type=varying, format=V}"
        type_varying_format_VB = "{type=varying, format=VB}"
        type_varying_format_VBS = "{type=varying, format=VBS}"
        type_varying_format_VR = "{type=varying, format=VR}"
        type_varying_format_VS = "{type=varying, format=VS}"

    class Delimiter(Enum):
        """Enum for the Delimiter property."""

        custom = " "
        ws = "ws"
        end = "end"
        none = "none"
        null = "null"
        comma = "','"
        tab = "'\t'"

    class Quote(Enum):
        """Enum for the Quote property."""

        custom = " "
        single = "single"
        double = "double"
        none = "none"

    class NullFieldValueSeparator(Enum):
        """Enum for the NullFieldValueSeparator property."""

        space = " "
        comma = "','"

    class PrintField(Enum):
        """Enum for the PrintField property."""

        print_field = "print_field"

    class VectorPrefix(Enum):
        """Enum for the VectorPrefix property."""

        one = 1
        two = 2
        four = 4

    class PrefixBytes(Enum):
        """Enum for the PrefixBytes property."""

        one = 1
        two = 2
        four = 4

    class ByteOrder(Enum):
        """Enum for the ByteOrder property."""

        little_endian = "little_endian"
        big_endian = "big_endian"
        native_endian = "native_endian"

    class CharacterSet(Enum):
        """Enum for the CharacterSet property."""

        ebcdic = "ebcdic"
        ascii = "ascii"

    class DataFormat(Enum):
        """Enum for the DataFormat property."""

        binary = "binary"
        text = "text"

    class PadChar(Enum):
        """Enum for the PadChar property."""

        custom = " "
        false_ = "' '"
        null = "null"

    class ExportEbcdicAsAscii(Enum):
        """Enum for the ExportEbcdicAsAscii property."""

        export_ebcdic_as_ascii = "export_ebcdic_as_ascii"

    class ImportAsciiAsEbcdic(Enum):
        """Enum for the ImportAsciiAsEbcdic property."""

        import_ascii_as_ebcdic = "import_ascii_as_ebcdic"

    class AllowAllZeros(Enum):
        """Enum for the AllowAllZeros property."""

        nofix_zero = "nofix_zero"
        fix_zero = "fix_zero"

    class DecimalSeparator(Enum):
        """Enum for the DecimalSeparator property."""

        custom = " "
        comma = "','"
        period = "'.'"

    class DecimalPacked(Enum):
        """Enum for the DecimalPacked property."""

        packed = "packed"
        separate = "separate"
        zoned = "zoned"
        overpunch = "overpunch"

    class DecimalPackedCheck(Enum):
        """Enum for the DecimalPackedCheck property."""

        check = "check"
        nocheck = "nocheck"

    class DecimalPackedSigned(Enum):
        """Enum for the DecimalPackedSigned property."""

        signed = "signed"
        unsigned = "unsigned"

    class AllowSignedImport(Enum):
        """Enum for the AllowSignedImport property."""

        allow_signed_import = "allow_signed_import"

    class DecimalPackedSignPosition(Enum):
        """Enum for the DecimalPackedSignPosition property."""

        trailing = "trailing"
        leading = "leading"

    class Rounding(Enum):
        """Enum for the Rounding property."""

        ceil = "ceil"
        floor = "floor"
        round_inf = "round_inf"
        trunc_zero = "trunc_zero"

    class IsJulian(Enum):
        """Enum for the IsJulian property."""

        julian = "julian"

    class IsMidnightSeconds(Enum):
        """Enum for the IsMidnightSeconds property."""

        midnight_seconds = "midnight_seconds"

    class RecLevelOption(Enum):
        """Enum for the RecLevelOption property."""

        final_delimiter = "final_delimiter"
        fill = "fill"
        final_delim_string = "final_delim_string"
        intact = "intact"
        record_delimiter = "record_delimiter"
        record_delim_string = "record_delim_string"
        record_length = "record_length"
        record_prefix = "record_prefix"
        record_format = "record_format"

    class FieldOption(Enum):
        """Enum for the FieldOption property."""

        delimiter = "delimiter"
        quote = "quote"
        actual_length = "actual_length"
        delim_string = "delim_string"
        null_length = "null_length"
        null_field = "null_field"
        prefix_bytes = "prefix_bytes"
        print_field = "print_field"
        vector_prefix = "vector_prefix"

    class GeneralOption(Enum):
        """Enum for the GeneralOption property."""

        byte_order = "byte_order"
        charset = "charset"
        data_format = "data_format"
        max_width = "max_width"
        field_width = "field_width"
        padchar = "padchar"

    class StringOption(Enum):
        """Enum for the StringOption property."""

        export_ebcdic_as_ascii = "export_ebcdic_as_ascii"
        import_ascii_as_ebcdic = "import_ascii_as_ebcdic"

    class DecimalOption(Enum):
        """Enum for the DecimalOption property."""

        allow_all_zeros = "allow_all_zeros"
        decimal_separator = "decimal_separator"
        decimal_packed = "decimal_packed"
        precision = "precision"
        round = "round"
        scale = "scale"

    class NumericOption(Enum):
        """Enum for the NumericOption property."""

        c_format = "c_format"
        in_format = "in_format"
        out_format = "out_format"

    class DateOption(Enum):
        """Enum for the DateOption property."""

        none = "none"
        days_since = "days_since"
        date_format = "date_format"
        is_julian = "is_julian"

    class TimeOption(Enum):
        """Enum for the TimeOption property."""

        none = "none"
        time_format = "time_format"
        is_midnight_seconds = "is_midnight_seconds"

    class TimestampOption(Enum):
        """Enum for the TimestampOption property."""

        none = "none"
        timestamp_format = "timestamp_format"

    class Collate(Enum):
        """Enum for the Collate property."""

        OFF = "OFF"
        af = "af"
        af_NA = "af_NA"
        af_ZA = "af_ZA"
        agq = "agq"
        agq_CM = "agq_CM"
        ak = "ak"
        ak_GH = "ak_GH"
        am = "am"
        am_ET = "am_ET"
        ar = "ar"
        ar_001 = "ar_001"
        ar_AE = "ar_AE"
        ar_BH = "ar_BH"
        ar_DJ = "ar_DJ"
        ar_DZ = "ar_DZ"
        ar_EG = "ar_EG"
        ar_EH = "ar_EH"
        ar_ER = "ar_ER"
        ar_IL = "ar_IL"
        ar_IQ = "ar_IQ"
        ar_JO = "ar_JO"
        ar_KM = "ar_KM"
        ar_KW = "ar_KW"
        ar_LB = "ar_LB"
        ar_LY = "ar_LY"
        ar_MA = "ar_MA"
        ar_MR = "ar_MR"
        ar_OM = "ar_OM"
        ar_PS = "ar_PS"
        ar_QA = "ar_QA"
        ar_SA = "ar_SA"
        ar_SD = "ar_SD"
        ar_SO = "ar_SO"
        ar_SY = "ar_SY"
        ar_TD = "ar_TD"
        ar_TN = "ar_TN"
        ar_YE = "ar_YE"
        as_ = "as"
        as_IN = "as_IN"
        asa = "asa"
        asa_TZ = "asa_TZ"
        az = "az"
        az_Cyrl = "az_Cyrl"
        az_Cyrl_AZ = "az_Cyrl_AZ"
        az_Latn = "az_Latn"
        az_Latn_AZ = "az_Latn_AZ"
        bas = "bas"
        bas_CM = "bas_CM"
        be = "be"
        be_BY = "be_BY"
        bem = "bem"
        bem_ZM = "bem_ZM"
        bez = "bez"
        bez_TZ = "bez_TZ"
        bg = "bg"
        bg_BG = "bg_BG"
        bm = "bm"
        bm_ML = "bm_ML"
        bn = "bn"
        bn_BD = "bn_BD"
        bn_IN = "bn_IN"
        bo = "bo"
        bo_CN = "bo_CN"
        bo_IN = "bo_IN"
        br = "br"
        br_FR = "br_FR"
        brx = "brx"
        brx_IN = "brx_IN"
        bs = "bs"
        bs_Cyrl = "bs_Cyrl"
        bs_Cyrl_BA = "bs_Cyrl_BA"
        bs_Latn = "bs_Latn"
        bs_Latn_BA = "bs_Latn_BA"
        ca = "ca"
        ca_AD = "ca_AD"
        ca_ES = "ca_ES"
        cgg = "cgg"
        cgg_UG = "cgg_UG"
        chr = "chr"
        chr_US = "chr_US"
        cs = "cs"
        cs_CZ = "cs_CZ"
        cy = "cy"
        cy_GB = "cy_GB"
        da = "da"
        da_DK = "da_DK"
        dav = "dav"
        dav_KE = "dav_KE"
        de = "de"
        de_AT = "de_AT"
        de_BE = "de_BE"
        de_CH = "de_CH"
        de_DE = "de_DE"
        de_LI = "de_LI"
        de_LU = "de_LU"
        dje = "dje"
        dje_NE = "dje_NE"
        dua = "dua"
        dua_CM = "dua_CM"
        dyo = "dyo"
        dyo_SN = "dyo_SN"
        dz = "dz"
        dz_BT = "dz_BT"
        ebu = "ebu"
        ebu_KE = "ebu_KE"
        ee = "ee"
        ee_GH = "ee_GH"
        ee_TG = "ee_TG"
        el = "el"
        el_CY = "el_CY"
        el_GR = "el_GR"
        en = "en"
        en_150 = "en_150"
        en_AG = "en_AG"
        en_AS = "en_AS"
        en_AU = "en_AU"
        en_BB = "en_BB"
        en_BE = "en_BE"
        en_BM = "en_BM"
        en_BS = "en_BS"
        en_BW = "en_BW"
        en_BZ = "en_BZ"
        en_CA = "en_CA"
        en_CM = "en_CM"
        en_DM = "en_DM"
        en_FJ = "en_FJ"
        en_FM = "en_FM"
        en_GB = "en_GB"
        en_GD = "en_GD"
        en_GG = "en_GG"
        en_GH = "en_GH"
        en_GI = "en_GI"
        en_GM = "en_GM"
        en_GU = "en_GU"
        en_GY = "en_GY"
        en_HK = "en_HK"
        en_IE = "en_IE"
        en_IM = "en_IM"
        en_IN = "en_IN"
        en_JE = "en_JE"
        en_JM = "en_JM"
        en_KE = "en_KE"
        en_KI = "en_KI"
        en_KN = "en_KN"
        en_KY = "en_KY"
        en_LC = "en_LC"
        en_LR = "en_LR"
        en_LS = "en_LS"
        en_MG = "en_MG"
        en_MH = "en_MH"
        en_MP = "en_MP"
        en_MT = "en_MT"
        en_MU = "en_MU"
        en_MW = "en_MW"
        en_NA = "en_NA"
        en_NG = "en_NG"
        en_NZ = "en_NZ"
        en_PG = "en_PG"
        en_PH = "en_PH"
        en_PK = "en_PK"
        en_PR = "en_PR"
        en_PW = "en_PW"
        en_SB = "en_SB"
        en_SC = "en_SC"
        en_SG = "en_SG"
        en_SL = "en_SL"
        en_SS = "en_SS"
        en_SZ = "en_SZ"
        en_TC = "en_TC"
        en_TO = "en_TO"
        en_TT = "en_TT"
        en_TZ = "en_TZ"
        en_UG = "en_UG"
        en_UM = "en_UM"
        en_US = "en_US"
        en_US_POSIX = "en_US_POSIX"
        en_VC = "en_VC"
        en_VG = "en_VG"
        en_VI = "en_VI"
        en_VU = "en_VU"
        en_WS = "en_WS"
        en_ZA = "en_ZA"
        en_ZM = "en_ZM"
        en_ZW = "en_ZW"
        eo = "eo"
        es = "es"
        es_419 = "es_419"
        es_AR = "es_AR"
        es_BO = "es_BO"
        es_CL = "es_CL"
        es_CO = "es_CO"
        es_CR = "es_CR"
        es_CU = "es_CU"
        es_DO = "es_DO"
        es_EA = "es_EA"
        es_EC = "es_EC"
        es_ES = "es_ES"
        es_GQ = "es_GQ"
        es_GT = "es_GT"
        es_HN = "es_HN"
        es_IC = "es_IC"
        es_MX = "es_MX"
        es_NI = "es_NI"
        es_PA = "es_PA"
        es_PE = "es_PE"
        es_PH = "es_PH"
        es_PR = "es_PR"
        es_PY = "es_PY"
        es_SV = "es_SV"
        es_US = "es_US"
        es_UY = "es_UY"
        es_VE = "es_VE"
        et = "et"
        et_EE = "et_EE"
        eu = "eu"
        eu_ES = "eu_ES"
        ewo = "ewo"
        ewo_CM = "ewo_CM"
        fa = "fa"
        fa_AF = "fa_AF"
        fa_IR = "fa_IR"
        ff = "ff"
        ff_SN = "ff_SN"
        fi = "fi"
        fi_FI = "fi_FI"
        fil = "fil"
        fil_PH = "fil_PH"
        fo = "fo"
        fo_FO = "fo_FO"
        fr = "fr"
        fr_BE = "fr_BE"
        fr_BF = "fr_BF"
        fr_BI = "fr_BI"
        fr_BJ = "fr_BJ"
        fr_BL = "fr_BL"
        fr_CA = "fr_CA"
        fr_CD = "fr_CD"
        fr_CF = "fr_CF"
        fr_CG = "fr_CG"
        fr_CH = "fr_CH"
        fr_CI = "fr_CI"
        fr_CM = "fr_CM"
        fr_DJ = "fr_DJ"
        fr_DZ = "fr_DZ"
        fr_FR = "fr_FR"
        fr_GA = "fr_GA"
        fr_GF = "fr_GF"
        fr_GN = "fr_GN"
        fr_GP = "fr_GP"
        fr_GQ = "fr_GQ"
        fr_HT = "fr_HT"
        fr_KM = "fr_KM"
        fr_LU = "fr_LU"
        fr_MA = "fr_MA"
        fr_MC = "fr_MC"
        fr_MF = "fr_MF"
        fr_MG = "fr_MG"
        fr_ML = "fr_ML"
        fr_MQ = "fr_MQ"
        fr_MR = "fr_MR"
        fr_MU = "fr_MU"
        fr_NC = "fr_NC"
        fr_NE = "fr_NE"
        fr_PF = "fr_PF"
        fr_RE = "fr_RE"
        fr_RW = "fr_RW"
        fr_SC = "fr_SC"
        fr_SN = "fr_SN"
        fr_SY = "fr_SY"
        fr_TD = "fr_TD"
        fr_TG = "fr_TG"
        fr_TN = "fr_TN"
        fr_VU = "fr_VU"
        fr_YT = "fr_YT"
        ga = "ga"
        ga_IE = "ga_IE"
        gl = "gl"
        gl_ES = "gl_ES"
        gsw = "gsw"
        gsw_CH = "gsw_CH"
        gu = "gu"
        gu_IN = "gu_IN"
        guz = "guz"
        guz_KE = "guz_KE"
        gv = "gv"
        gv_GB = "gv_GB"
        ha = "ha"
        ha_Latn = "ha_Latn"
        ha_Latn_GH = "ha_Latn_GH"
        ha_Latn_NE = "ha_Latn_NE"
        ha_Latn_NG = "ha_Latn_NG"
        haw = "haw"
        haw_US = "haw_US"
        he = "he"
        he_IL = "he_IL"
        hi = "hi"
        hi_IN = "hi_IN"
        hr = "hr"
        hr_BA = "hr_BA"
        hr_HR = "hr_HR"
        hu = "hu"
        hu_HU = "hu_HU"
        hy = "hy"
        hy_AM = "hy_AM"
        id = "id"
        id_ID = "id_ID"
        ig = "ig"
        ig_NG = "ig_NG"
        ii = "ii"
        ii_CN = "ii_CN"
        is_ = "is"
        is_IS = "is_IS"
        it = "it"
        it_CH = "it_CH"
        it_IT = "it_IT"
        it_SM = "it_SM"
        ja = "ja"
        ja_JP = "ja_JP"
        jgo = "jgo"
        jgo_CM = "jgo_CM"
        jmc = "jmc"
        jmc_TZ = "jmc_TZ"
        ka = "ka"
        ka_GE = "ka_GE"
        kab = "kab"
        kab_DZ = "kab_DZ"
        kam = "kam"
        kam_KE = "kam_KE"
        kde = "kde"
        kde_TZ = "kde_TZ"
        kea = "kea"
        kea_CV = "kea_CV"
        khq = "khq"
        khq_ML = "khq_ML"
        ki = "ki"
        ki_KE = "ki_KE"
        kk = "kk"
        kk_Cyrl = "kk_Cyrl"
        kk_Cyrl_KZ = "kk_Cyrl_KZ"
        kl = "kl"
        kl_GL = "kl_GL"
        kln = "kln"
        kln_KE = "kln_KE"
        km = "km"
        km_KH = "km_KH"
        kn = "kn"
        kn_IN = "kn_IN"
        ko = "ko"
        ko_KP = "ko_KP"
        ko_KR = "ko_KR"
        kok = "kok"
        kok_IN = "kok_IN"
        ks = "ks"
        ks_Arab = "ks_Arab"
        ks_Arab_IN = "ks_Arab_IN"
        ksb = "ksb"
        ksb_TZ = "ksb_TZ"
        ksf = "ksf"
        ksf_CM = "ksf_CM"
        kw = "kw"
        kw_GB = "kw_GB"
        lag = "lag"
        lag_TZ = "lag_TZ"
        lg = "lg"
        lg_UG = "lg_UG"
        ln = "ln"
        ln_AO = "ln_AO"
        ln_CD = "ln_CD"
        ln_CF = "ln_CF"
        ln_CG = "ln_CG"
        lo = "lo"
        lo_LA = "lo_LA"
        lt = "lt"
        lt_LT = "lt_LT"
        lu = "lu"
        lu_CD = "lu_CD"
        luo = "luo"
        luo_KE = "luo_KE"
        luy = "luy"
        luy_KE = "luy_KE"
        lv = "lv"
        lv_LV = "lv_LV"
        mas = "mas"
        mas_KE = "mas_KE"
        mas_TZ = "mas_TZ"
        mer = "mer"
        mer_KE = "mer_KE"
        mfe = "mfe"
        mfe_MU = "mfe_MU"
        mg = "mg"
        mg_MG = "mg_MG"
        mgh = "mgh"
        mgh_MZ = "mgh_MZ"
        mgo = "mgo"
        mgo_CM = "mgo_CM"
        mk = "mk"
        mk_MK = "mk_MK"
        ml = "ml"
        ml_IN = "ml_IN"
        mr = "mr"
        mr_IN = "mr_IN"
        ms = "ms"
        ms_BN = "ms_BN"
        ms_MY = "ms_MY"
        ms_SG = "ms_SG"
        mt = "mt"
        mt_MT = "mt_MT"
        mua = "mua"
        mua_CM = "mua_CM"
        my = "my"
        my_MM = "my_MM"
        naq = "naq"
        naq_NA = "naq_NA"
        nb = "nb"
        nb_NO = "nb_NO"
        nd = "nd"
        nd_ZW = "nd_ZW"
        ne = "ne"
        ne_IN = "ne_IN"
        ne_NP = "ne_NP"
        nl = "nl"
        nl_AW = "nl_AW"
        nl_BE = "nl_BE"
        nl_CW = "nl_CW"
        nl_NL = "nl_NL"
        nl_SR = "nl_SR"
        nl_SX = "nl_SX"
        nmg = "nmg"
        nmg_CM = "nmg_CM"
        nn = "nn"
        nn_NO = "nn_NO"
        nus = "nus"
        nus_SD = "nus_SD"
        nyn = "nyn"
        nyn_UG = "nyn_UG"
        om = "om"
        om_ET = "om_ET"
        om_KE = "om_KE"
        or_ = "or"
        or_IN = "or_IN"
        pa = "pa"
        pa_Arab = "pa_Arab"
        pa_Arab_PK = "pa_Arab_PK"
        pa_Guru = "pa_Guru"
        pa_Guru_IN = "pa_Guru_IN"
        pl = "pl"
        pl_PL = "pl_PL"
        ps = "ps"
        ps_AF = "ps_AF"
        pt = "pt"
        pt_AO = "pt_AO"
        pt_BR = "pt_BR"
        pt_CV = "pt_CV"
        pt_GW = "pt_GW"
        pt_MO = "pt_MO"
        pt_MZ = "pt_MZ"
        pt_PT = "pt_PT"
        pt_ST = "pt_ST"
        pt_TL = "pt_TL"
        rm = "rm"
        rm_CH = "rm_CH"
        rn = "rn"
        rn_BI = "rn_BI"
        ro = "ro"
        ro_MD = "ro_MD"
        ro_RO = "ro_RO"
        rof = "rof"
        rof_TZ = "rof_TZ"
        ru = "ru"
        ru_BY = "ru_BY"
        ru_KG = "ru_KG"
        ru_KZ = "ru_KZ"
        ru_MD = "ru_MD"
        ru_RU = "ru_RU"
        ru_UA = "ru_UA"
        rw = "rw"
        rw_RW = "rw_RW"
        rwk = "rwk"
        rwk_TZ = "rwk_TZ"
        saq = "saq"
        saq_KE = "saq_KE"
        sbp = "sbp"
        sbp_TZ = "sbp_TZ"
        seh = "seh"
        seh_MZ = "seh_MZ"
        ses = "ses"
        ses_ML = "ses_ML"
        sg = "sg"
        sg_CF = "sg_CF"
        shi = "shi"
        shi_Latn = "shi_Latn"
        shi_Latn_MA = "shi_Latn_MA"
        shi_Tfng = "shi_Tfng"
        shi_Tfng_MA = "shi_Tfng_MA"
        si = "si"
        si_LK = "si_LK"
        sk = "sk"
        sk_SK = "sk_SK"
        sl = "sl"
        sl_SI = "sl_SI"
        sn = "sn"
        sn_ZW = "sn_ZW"
        so = "so"
        so_DJ = "so_DJ"
        so_ET = "so_ET"
        so_KE = "so_KE"
        so_SO = "so_SO"
        sq = "sq"
        sq_AL = "sq_AL"
        sq_MK = "sq_MK"
        sr = "sr"
        sr_Cyrl = "sr_Cyrl"
        sr_Cyrl_BA = "sr_Cyrl_BA"
        sr_Cyrl_ME = "sr_Cyrl_ME"
        sr_Cyrl_RS = "sr_Cyrl_RS"
        sr_Latn = "sr_Latn"
        sr_Latn_BA = "sr_Latn_BA"
        sr_Latn_ME = "sr_Latn_ME"
        sr_Latn_RS = "sr_Latn_RS"
        sv = "sv"
        sv_AX = "sv_AX"
        sv_FI = "sv_FI"
        sv_SE = "sv_SE"
        sw = "sw"
        sw_KE = "sw_KE"
        sw_TZ = "sw_TZ"
        sw_UG = "sw_UG"
        swc = "swc"
        swc_CD = "swc_CD"
        ta = "ta"
        ta_IN = "ta_IN"
        ta_LK = "ta_LK"
        ta_MY = "ta_MY"
        ta_SG = "ta_SG"
        te = "te"
        te_IN = "te_IN"
        teo = "teo"
        teo_KE = "teo_KE"
        teo_UG = "teo_UG"
        th = "th"
        th_TH = "th_TH"
        ti = "ti"
        ti_ER = "ti_ER"
        ti_ET = "ti_ET"
        to = "to"
        to_TO = "to_TO"
        tr = "tr"
        tr_CY = "tr_CY"
        tr_TR = "tr_TR"
        twq = "twq"
        twq_NE = "twq_NE"
        tzm = "tzm"
        tzm_Latn = "tzm_Latn"
        tzm_Latn_MA = "tzm_Latn_MA"
        uk = "uk"
        uk_UA = "uk_UA"
        ur = "ur"
        ur_IN = "ur_IN"
        ur_PK = "ur_PK"
        uz = "uz"
        uz_Arab = "uz_Arab"
        uz_Arab_AF = "uz_Arab_AF"
        uz_Cyrl = "uz_Cyrl"
        uz_Cyrl_UZ = "uz_Cyrl_UZ"
        uz_Latn = "uz_Latn"
        uz_Latn_UZ = "uz_Latn_UZ"
        vai = "vai"
        vai_Latn = "vai_Latn"
        vai_Latn_LR = "vai_Latn_LR"
        vai_Vaii = "vai_Vaii"
        vai_Vaii_LR = "vai_Vaii_LR"
        vi = "vi"
        vi_VN = "vi_VN"
        vun = "vun"
        vun_TZ = "vun_TZ"
        xog = "xog"
        xog_UG = "xog_UG"
        yav = "yav"
        yav_CM = "yav_CM"
        yo = "yo"
        yo_NG = "yo_NG"
        zh = "zh"
        zh_Hans = "zh_Hans"
        zh_Hans_CN = "zh_Hans_CN"
        zh_Hans_HK = "zh_Hans_HK"
        zh_Hans_MO = "zh_Hans_MO"
        zh_Hans_SG = "zh_Hans_SG"
        zh_Hant = "zh_Hant"
        zh_Hant_HK = "zh_Hant_HK"
        zh_Hant_MO = "zh_Hant_MO"
        zh_Hant_TW = "zh_Hant_TW"
        zu = "zu"
        zu_ZA = "zu_ZA"


class COPY:
    """Enums for properties in the COPY stage."""

    class Force(Enum):
        """Enum for the Force property."""

        false = " "
        true = "force"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class GENERIC:
    """Enums for properties in the GENERIC stage."""

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class MAKE_SUBRECORD:
    """Enums for properties in the MAKE_SUBRECORD stage."""

    class Variable(Enum):
        """Enum for the Variable property."""

        true = "variable"
        false = " "

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class COMPLEX_FLAT_FILE:
    """Enums for properties in the COMPLEX_FLAT_FILE stage."""

    class Charset(Enum):
        """Enum for the Charset property."""

        custom = " "
        ebcdic = "ebcdic"
        ascii = "ascii"

    class Rejects(Enum):
        """Enum for the Rejects property."""

        save = "save"
        cont = "continue"
        fail = "fail"

    class Decrounding(Enum):
        """Enum for the Decrounding property."""

        round_inf = "round_inf"
        floor = "floor"
        ceil = "ceil"
        trunc_zero = "trunc_zero"

    class MissingFile(Enum):
        """Enum for the MissingFile property."""

        error = "error"
        custom = " "
        okay = "okay"

    class Recordtype(Enum):
        """Enum for the Recordtype property."""

        V = "V"
        FB = "FB"
        VB = "VB"
        VS = "VS"
        F = "F"
        VBS = "VBS"
        VR = "VR"

    class Recorddelimiter(Enum):
        """Enum for the Recorddelimiter property."""

        custom = " "
        null = "null"
        newline = "newline"

    class Nocleanup(Enum):
        """Enum for the Nocleanup property."""

        true = "nocleanup"
        false = " "

    class Byteorder(Enum):
        """Enum for the Byteorder property."""

        big_endian = "big_endian"
        little_endian = "little_endian"
        native_endian = "native_endian"

    class FieldRejects(Enum):
        """Enum for the FieldRejects property."""

        saveRejects = "saveRejects"
        keepField = "keepField"
        failRejects = "failRejects"

    class ConnectToZos(Enum):
        """Enum for the ConnectToZos property."""

        custom = " "
        zosAsSource = "zosAsSource"
        zosAsTarget = "zosAsTarget"

    class Allowzeros(Enum):
        """Enum for the Allowzeros property."""

        nofix_zero = "nofix_zero"
        fix_zero = "fix_zero"

    class Multinode(Enum):
        """Enum for the Multinode property."""

        no = " "
        yes = "yes"

    class Dataformat(Enum):
        """Enum for the Dataformat property."""

        text = "text"
        binary = "binary"

    class Writeoption(Enum):
        """Enum for the Writeoption property."""

        overwrite = "overwrite"
        append = "append"
        custom = " "

    class KeepPartitions(Enum):
        """Enum for the KeepPartitions property."""

        false = " "
        true = "keepPartitions"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        minus_one = "-1"
        set = "1"
        minus_two = "-2"
        clear = "0"

    class RecordPrefix(Enum):
        """Enum for the RecordPrefix property."""

        custom = " "
        one = "1"
        two = "2"
        four = "4"

    class Floatrepresentation(Enum):
        """Enum for the Floatrepresentation property."""

        IEEE = "IEEE"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        combine = "combine"
        nocombine = "nocombine"
        auto = "auto"

    class Selection(Enum):
        """Enum for the Selection property."""

        sourcelist = "sourcelist"
        destination = "destination"
        destinationlist = "destinationlist"
        filepattern = "filepattern"
        singlefile = "singlefile"
        source = "source"
        multifile = "multifile"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        default_seq = "default_seq"

    class PrintField(Enum):
        """Enum for the PrintField property."""

        false = " "
        true = "print_field"

    class ReportProgress(Enum):
        """Enum for the ReportProgress property."""

        no = "no"
        yes = "yes"

    class Decsep(Enum):
        """Enum for the Decsep property."""

        dot = "."
        comma = ","
        default = "default"

    class NlsMapName(Enum):
        """Enum for the NlsMapName property."""

        Adobe_Standard_Encoding = "Adobe-Standard-Encoding"
        ANSI_X3_4_1968 = "ANSI_X3.4-1968"
        ASCL_ASCII = "ASCL_ASCII"
        ASCL_ASCII_PC1 = "ASCL_ASCII-PC1"
        ASCL_BIG5 = "ASCL_BIG5"
        ASCL_C0_CONTROLS = "ASCL_C0-CONTROLS"
        ASCL_C1_CONTROLS = "ASCL_C1-CONTROLS"
        ASCL_EBCDIC = "ASCL_EBCDIC"
        ASCL_EBCDIC_037 = "ASCL_EBCDIC-037"
        ASCL_EBCDIC_1026 = "ASCL_EBCDIC-1026"
        ASCL_EBCDIC_500V1 = "ASCL_EBCDIC-500V1"
        ASCL_EBCDIC_875 = "ASCL_EBCDIC-875"
        ASCL_EBCDIC_CTRLS = "ASCL_EBCDIC-CTRLS"
        ASCL_EBCDIC_IBM1364 = "ASCL_EBCDIC-IBM1364"
        ASCL_EBCDIC_IBM1371 = "ASCL_EBCDIC-IBM1371"
        ASCL_EBCDIC_IBM933 = "ASCL_EBCDIC-IBM933"
        ASCL_EBCDIC_IBM937 = "ASCL_EBCDIC-IBM937"
        ASCL_EBCDIC_JP_CTRLS = "ASCL_EBCDIC-JP-CTRLS"
        ASCL_EBCDIC_JP_KANA = "ASCL_EBCDIC-JP-KANA"
        ASCL_EBCDIC_JP_KANA_E = "ASCL_EBCDIC-JP-KANA-E"
        ASCL_EBCDIC_JP_KANA_HW = "ASCL_EBCDIC-JP-KANA-HW"
        ASCL_GB2312 = "ASCL_GB2312"
        ASCL_ISO8859_1 = "ASCL_ISO8859-1"
        ASCL_ISO8859_10 = "ASCL_ISO8859-10"
        ASCL_ISO8859_15 = "ASCL_ISO8859-15"
        ASCL_ISO8859_2 = "ASCL_ISO8859-2"
        ASCL_ISO8859_3 = "ASCL_ISO8859-3"
        ASCL_ISO8859_4 = "ASCL_ISO8859-4"
        ASCL_ISO8859_5 = "ASCL_ISO8859-5"
        ASCL_ISO8859_6 = "ASCL_ISO8859-6"
        ASCL_ISO8859_7 = "ASCL_ISO8859-7"
        ASCL_ISO8859_8 = "ASCL_ISO8859-8"
        ASCL_ISO8859_9 = "ASCL_ISO8859-9"
        ASCL_JIS_EUC = "ASCL_JIS-EUC"
        ASCL_JIS_EUC_HWK = "ASCL_JIS-EUC-HWK"
        ASCL_JIS_EUC_P = "ASCL_JIS-EUC-P"
        ASCL_JIS_ROMAN = "ASCL_JIS-ROMAN"
        ASCL_JISX0201 = "ASCL_JISX0201"
        ASCL_JPN_EBCDIC = "ASCL_JPN-EBCDIC"
        ASCL_JPN_EBCDIK = "ASCL_JPN-EBCDIK"
        ASCL_JPN_EBCDIKC_CTRL = "ASCL_JPN-EBCDIKC-CTRL"
        ASCL_JPN_EUC = "ASCL_JPN-EUC"
        ASCL_JPN_EUC_KAT = "ASCL_JPN-EUC-KAT"
        ASCL_JPN_EUC_ONE = "ASCL_JPN-EUC-ONE"
        ASCL_JPN_EUC_RTE = "ASCL_JPN-EUC-RTE"
        ASCL_JPN_EUC_TWO = "ASCL_JPN-EUC-TWO"
        ASCL_JPN_IBM78 = "ASCL_JPN-IBM78"
        ASCL_JPN_IBM83 = "ASCL_JPN-IBM83"
        ASCL_JPN_JEF78 = "ASCL_JPN-JEF78"
        ASCL_JPN_JEF83 = "ASCL_JPN-JEF83"
        ASCL_JPN_JIPSE = "ASCL_JPN-JIPSE"
        ASCL_JPN_JIPSJ = "ASCL_JPN-JIPSJ"
        ASCL_JPN_JIS_RTE = "ASCL_JPN-JIS-RTE"
        ASCL_JPN_JIS8 = "ASCL_JPN-JIS8"
        ASCL_JPN_JIS8EUC_CTRL = "ASCL_JPN-JIS8EUC-CTRL"
        ASCL_JPN_KEIS_RTE = "ASCL_JPN-KEIS-RTE"
        ASCL_JPN_KEIS78 = "ASCL_JPN-KEIS78"
        ASCL_JPN_KEIS83 = "ASCL_JPN-KEIS83"
        ASCL_JPN_NEBCDIK = "ASCL_JPN-NEBCDIK"
        ASCL_JPN_SJIS = "ASCL_JPN-SJIS"
        ASCL_KOI8_R = "ASCL_KOI8-R"
        ASCL_KSC5601 = "ASCL_KSC5601"
        ASCL_KSC5601_1992 = "ASCL_KSC5601-1992"
        ASCL_MAC_GREEK = "ASCL_MAC-GREEK"
        ASCL_MAC_GREEK2 = "ASCL_MAC-GREEK2"
        ASCL_MAC_ROMAN = "ASCL_MAC-ROMAN"
        ASCL_MNEMONICS = "ASCL_MNEMONICS"
        ASCL_MS1250 = "ASCL_MS1250"
        ASCL_MS1251 = "ASCL_MS1251"
        ASCL_MS1252 = "ASCL_MS1252"
        ASCL_MS1253 = "ASCL_MS1253"
        ASCL_MS1254 = "ASCL_MS1254"
        ASCL_MS1255 = "ASCL_MS1255"
        ASCL_MS1256 = "ASCL_MS1256"
        ASCL_MS932 = "ASCL_MS932"
        ASCL_MS932_BASE = "ASCL_MS932-BASE"
        ASCL_MS932_EXTRA = "ASCL_MS932-EXTRA"
        ASCL_MS936 = "ASCL_MS936"
        ASCL_MS936_BASE = "ASCL_MS936-BASE"
        ASCL_MS949 = "ASCL_MS949"
        ASCL_MS950 = "ASCL_MS950"
        ASCL_MS950_BASE = "ASCL_MS950-BASE"
        ASCL_PC1040 = "ASCL_PC1040"
        ASCL_PC1041 = "ASCL_PC1041"
        ASCL_PC437 = "ASCL_PC437"
        ASCL_PC850 = "ASCL_PC850"
        ASCL_PC852 = "ASCL_PC852"
        ASCL_PC855 = "ASCL_PC855"
        ASCL_PC857 = "ASCL_PC857"
        ASCL_PC860 = "ASCL_PC860"
        ASCL_PC861 = "ASCL_PC861"
        ASCL_PC862 = "ASCL_PC862"
        ASCL_PC863 = "ASCL_PC863"
        ASCL_PC864 = "ASCL_PC864"
        ASCL_PC865 = "ASCL_PC865"
        ASCL_PC866 = "ASCL_PC866"
        ASCL_PC869 = "ASCL_PC869"
        ASCL_PC874 = "ASCL_PC874"
        ASCL_PRIME_SHIFT_JIS = "ASCL_PRIME-SHIFT-JIS"
        ASCL_SHIFT_JIS = "ASCL_SHIFT-JIS"
        ASCL_TAU_SHIFT_JIS = "ASCL_TAU-SHIFT-JIS"
        ASCL_TIS620 = "ASCL_TIS620"
        ASCL_TIS620_B = "ASCL_TIS620-B"
        Big5 = "Big5"
        Big5_HKSCS = "Big5-HKSCS"
        BOCU_1 = "BOCU-1"
        CESU_8 = "CESU-8"
        ebcdic_xml_us = "ebcdic-xml-us"
        EUC_KR = "EUC-KR"
        GB_2312_80 = "GB_2312-80"
        gb18030_gb18030 = "gb18030 gb18030"
        GB2312 = "GB2312"
        GBK = "GBK"
        hp_roman8 = "hp-roman8"
        HZ_HZ_GB_2312 = "HZ HZ-GB-2312"
        ibm_1006_P100_1995 = "ibm-1006_P100-1995"
        ibm_1025_P100_1995 = "ibm-1025_P100-1995"
        ibm_1026_P100_1995 = "ibm-1026_P100-1995"
        ibm_1047_P100_1995 = "ibm-1047_P100-1995"
        ibm_1047_P100_1995_swaplfnl = "ibm-1047_P100-1995,swaplfnl"
        ibm_1051_P100_1995 = "ibm-1051_P100-1995"
        ibm_1089_P100_1995 = "ibm-1089_P100-1995"
        ibm_1097_P100_1995 = "ibm-1097_P100-1995"
        ibm_1098_P100_1995 = "ibm-1098_P100-1995"
        ibm_1112_P100_1995 = "ibm-1112_P100-1995"
        ibm_1122_P100_1999 = "ibm-1122_P100-1999"
        ibm_1123_P100_1995 = "ibm-1123_P100-1995"
        ibm_1124_P100_1996 = "ibm-1124_P100-1996"
        ibm_1125_P100_1997 = "ibm-1125_P100-1997"
        ibm_1129_P100_1997 = "ibm-1129_P100-1997"
        ibm_1130_P100_1997 = "ibm-1130_P100-1997"
        ibm_1131_P100_1997 = "ibm-1131_P100-1997"
        ibm_1132_P100_1998 = "ibm-1132_P100-1998"
        ibm_1133_P100_1997 = "ibm-1133_P100-1997"
        ibm_1137_P100_1999 = "ibm-1137_P100-1999"
        ibm_1140_P100_1997 = "ibm-1140_P100-1997"
        ibm_1140_P100_1997_swaplfnl = "ibm-1140_P100-1997,swaplfnl"
        ibm_1141_P100_1997 = "ibm-1141_P100-1997"
        ibm_1141_P100_1997_swaplfnl = "ibm-1141_P100-1997,swaplfnl"
        ibm_1142_P100_1997 = "ibm-1142_P100-1997"
        ibm_1142_P100_1997_swaplfnl = "ibm-1142_P100-1997,swaplfnl"
        ibm_1143_P100_1997 = "ibm-1143_P100-1997"
        ibm_1143_P100_1997_swaplfnl = "ibm-1143_P100-1997,swaplfnl"
        ibm_1144_P100_1997 = "ibm-1144_P100-1997"
        ibm_1144_P100_1997_swaplfnl = "ibm-1144_P100-1997,swaplfnl"
        ibm_1145_P100_1997 = "ibm-1145_P100-1997"
        ibm_1145_P100_1997_swaplfnl = "ibm-1145_P100-1997,swaplfnl"
        ibm_1146_P100_1997 = "ibm-1146_P100-1997"
        ibm_1146_P100_1997_swaplfnl = "ibm-1146_P100-1997,swaplfnl"
        ibm_1147_P100_1997 = "ibm-1147_P100-1997"
        ibm_1147_P100_1997_swaplfnl = "ibm-1147_P100-1997,swaplfnl"
        ibm_1148_P100_1997 = "ibm-1148_P100-1997"
        ibm_1148_P100_1997_swaplfnl = "ibm-1148_P100-1997,swaplfnl"
        ibm_1149_P100_1997 = "ibm-1149_P100-1997"
        ibm_1149_P100_1997_swaplfnl = "ibm-1149_P100-1997,swaplfnl"
        ibm_1153_P100_1999 = "ibm-1153_P100-1999"
        ibm_1153_P100_1999_swaplfnl = "ibm-1153_P100-1999,swaplfnl"
        ibm_1154_P100_1999 = "ibm-1154_P100-1999"
        ibm_1155_P100_1999 = "ibm-1155_P100-1999"
        ibm_1156_P100_1999 = "ibm-1156_P100-1999"
        ibm_1157_P100_1999 = "ibm-1157_P100-1999"
        ibm_1158_P100_1999 = "ibm-1158_P100-1999"
        ibm_1160_P100_1999 = "ibm-1160_P100-1999"
        ibm_1162_P100_1999 = "ibm-1162_P100-1999"
        ibm_1164_P100_1999 = "ibm-1164_P100-1999"
        ibm_1168_P100_2002 = "ibm-1168_P100-2002"
        ibm_1250_P100_1995 = "ibm-1250_P100-1995"
        ibm_1251_P100_1995 = "ibm-1251_P100-1995"
        ibm_1252_P100_2000 = "ibm-1252_P100-2000"
        ibm_1253_P100_1995 = "ibm-1253_P100-1995"
        ibm_1254_P100_1995 = "ibm-1254_P100-1995"
        ibm_1255_P100_1995 = "ibm-1255_P100-1995"
        ibm_1256_P110_1997 = "ibm-1256_P110-1997"
        ibm_1257_P100_1995 = "ibm-1257_P100-1995"
        ibm_1258_P100_1997 = "ibm-1258_P100-1997"
        ibm_12712_P100_1998 = "ibm-12712_P100-1998"
        ibm_12712_P100_1998_swaplfnl = "ibm-12712_P100-1998,swaplfnl"
        ibm_1276_P100_1995 = "ibm-1276_P100-1995"
        ibm_1277_P100_1995 = "ibm-1277_P100-1995"
        ibm_1363_P110_1997 = "ibm-1363_P110-1997"
        ibm_1363_P11B_1998 = "ibm-1363_P11B-1998"
        ibm_1364_P110_1997 = "ibm-1364_P110-1997"
        ibm_1364_P110_2007 = "ibm-1364_P110-2007"
        ibm_1371_P100_1999 = "ibm-1371_P100-1999"
        ibm_1373_P100_2002 = "ibm-1373_P100-2002"
        ibm_1375_P100_2003 = "ibm-1375_P100-2003"
        ibm_1375_P100_2007 = "ibm-1375_P100-2007"
        ibm_1381_P110_1999 = "ibm-1381_P110-1999"
        ibm_1383_P110_1999 = "ibm-1383_P110-1999"
        ibm_1386_P100_2001 = "ibm-1386_P100-2001"
        ibm_1386_P100_2002 = "ibm-1386_P100-2002"
        ibm_1388_P103_2001 = "ibm-1388_P103-2001"
        ibm_1390_P110_2003 = "ibm-1390_P110-2003"
        ibm_1399_P110_2003 = "ibm-1399_P110-2003"
        ibm_16684_P110_2003 = "ibm-16684_P110-2003"
        ibm_16804_X110_1999 = "ibm-16804_X110-1999"
        ibm_16804_X110_1999_swaplfnl = "ibm-16804_X110-1999,swaplfnl"
        ibm_273_P100_1995 = "ibm-273_P100-1995"
        ibm_277_P100_1995 = "ibm-277_P100-1995"
        ibm_278_P100_1995 = "ibm-278_P100-1995"
        ibm_280_P100_1995 = "ibm-280_P100-1995"
        ibm_284_P100_1995 = "ibm-284_P100-1995"
        ibm_285_P100_1995 = "ibm-285_P100-1995"
        ibm_290_P100_1995 = "ibm-290_P100-1995"
        ibm_297_P100_1995 = "ibm-297_P100-1995"
        ibm_33722_P120_1999 = "ibm-33722_P120-1999"
        ibm_33722_P12A_P12A_2009_U2_Extended_UNIX_Code_Packed_Format_for_Japanese = (
            "ibm-33722_P12A_P12A-2009_U2 Extended_UNIX_Code_Packed_Format_for_Japanese"
        )
        ibm_33722_P12A_1999 = "ibm-33722_P12A-1999"
        ibm_367_P100_1995 = "ibm-367_P100-1995"
        ibm_37_P100_1995 = "ibm-37_P100-1995"
        ibm_37_P100_1995_swaplfnl = "ibm-37_P100-1995,swaplfnl"
        ibm_420_X120_1999 = "ibm-420_X120-1999"
        ibm_424_P100_1995 = "ibm-424_P100-1995"
        ibm_437_P100_1995 = "ibm-437_P100-1995"
        ibm_4517_P100_2005 = "ibm-4517_P100-2005"
        ibm_4899_P100_1998 = "ibm-4899_P100-1998"
        ibm_4909_P100_1999 = "ibm-4909_P100-1999"
        ibm_4971_P100_1999 = "ibm-4971_P100-1999"
        ibm_500_P100_1995 = "ibm-500_P100-1995"
        ibm_5012_P100_1999 = "ibm-5012_P100-1999"
        ibm_5123_P100_1999 = "ibm-5123_P100-1999"
        ibm_5346_P100_1998 = "ibm-5346_P100-1998"
        ibm_5347_P100_1998 = "ibm-5347_P100-1998"
        ibm_5348_P100_1997 = "ibm-5348_P100-1997"
        ibm_5349_P100_1998 = "ibm-5349_P100-1998"
        ibm_5350_P100_1998 = "ibm-5350_P100-1998"
        ibm_5351_P100_1998 = "ibm-5351_P100-1998"
        ibm_5352_P100_1998 = "ibm-5352_P100-1998"
        ibm_5353_P100_1998 = "ibm-5353_P100-1998"
        ibm_5354_P100_1998 = "ibm-5354_P100-1998"
        ibm_5471_P100_2006 = "ibm-5471_P100-2006"
        ibm_5478_P100_1995 = "ibm-5478_P100-1995"
        ibm_720_P100_1997 = "ibm-720_P100-1997"
        ibm_737_P100_1997 = "ibm-737_P100-1997"
        ibm_775_P100_1996 = "ibm-775_P100-1996"
        ibm_803_P100_1999 = "ibm-803_P100-1999"
        ibm_813_P100_1995 = "ibm-813_P100-1995"
        ibm_838_P100_1995 = "ibm-838_P100-1995"
        ibm_8482_P100_1999 = "ibm-8482_P100-1999"
        ibm_850_P100_1995 = "ibm-850_P100-1995"
        ibm_851_P100_1995 = "ibm-851_P100-1995"
        ibm_852_P100_1995 = "ibm-852_P100-1995"
        ibm_855_P100_1995 = "ibm-855_P100-1995"
        ibm_856_P100_1995 = "ibm-856_P100-1995"
        ibm_857_P100_1995 = "ibm-857_P100-1995"
        ibm_858_P100_1997 = "ibm-858_P100-1997"
        ibm_860_P100_1995 = "ibm-860_P100-1995"
        ibm_861_P100_1995 = "ibm-861_P100-1995"
        ibm_862_P100_1995 = "ibm-862_P100-1995"
        ibm_863_P100_1995 = "ibm-863_P100-1995"
        ibm_864_X110_1999 = "ibm-864_X110-1999"
        ibm_865_P100_1995 = "ibm-865_P100-1995"
        ibm_866_P100_1995 = "ibm-866_P100-1995"
        ibm_867_P100_1998 = "ibm-867_P100-1998"
        ibm_868_P100_1995 = "ibm-868_P100-1995"
        ibm_869_P100_1995 = "ibm-869_P100-1995"
        ibm_870_P100_1995 = "ibm-870_P100-1995"
        ibm_871_P100_1995 = "ibm-871_P100-1995"
        ibm_874_P100_1995 = "ibm-874_P100-1995"
        ibm_875_P100_1995 = "ibm-875_P100-1995"
        ibm_878_P100_1996 = "ibm-878_P100-1996"
        ibm_897_P100_1995 = "ibm-897_P100-1995"
        ibm_9005_X110_2007 = "ibm-9005_X110-2007"
        ibm_901_P100_1999 = "ibm-901_P100-1999"
        ibm_902_P100_1999 = "ibm-902_P100-1999"
        ibm_9067_X100_2005 = "ibm-9067_X100-2005"
        ibm_912_P100_1995 = "ibm-912_P100-1995"
        ibm_913_P100_2000 = "ibm-913_P100-2000"
        ibm_914_P100_1995 = "ibm-914_P100-1995"
        ibm_915_P100_1995 = "ibm-915_P100-1995"
        ibm_916_P100_1995 = "ibm-916_P100-1995"
        ibm_918_P100_1995 = "ibm-918_P100-1995"
        ibm_920_P100_1995 = "ibm-920_P100-1995"
        ibm_921_P100_1995 = "ibm-921_P100-1995"
        ibm_922_P100_1999 = "ibm-922_P100-1999"
        ibm_923_P100_1998 = "ibm-923_P100-1998"
        ibm_930_P120_1999 = "ibm-930_P120-1999"
        ibm_933_P110_1995 = "ibm-933_P110-1995"
        ibm_935_P110_1999 = "ibm-935_P110-1999"
        ibm_937_P110_1999 = "ibm-937_P110-1999"
        ibm_939_P120_1999 = "ibm-939_P120-1999"
        ibm_942_P12A_1999 = "ibm-942_P12A-1999"
        ibm_943_P130_1999 = "ibm-943_P130-1999"
        ibm_943_P15A_2003 = "ibm-943_P15A-2003"
        ibm_9447_P100_2002 = "ibm-9447_P100-2002"
        ibm_9448_X100_2005 = "ibm-9448_X100-2005"
        ibm_9449_P100_2002 = "ibm-9449_P100-2002"
        ibm_949_P110_1999 = "ibm-949_P110-1999"
        ibm_949_P11A_1999 = "ibm-949_P11A-1999"
        ibm_950_P110_1999 = "ibm-950_P110-1999"
        ibm_954_P101_2000 = "ibm-954_P101-2000"
        ibm_954_P101_2007 = "ibm-954_P101-2007"
        ibm_964_P110_1999 = "ibm-964_P110-1999"
        ibm_970_P110_P110_2006_U2 = "ibm-970_P110_P110-2006_U2"
        ibm_970_P110_1995 = "ibm-970_P110-1995"
        ibm_971_P100_1995 = "ibm-971_P100-1995"
        IBM_Thai = "IBM-Thai"
        IBM00858 = "IBM00858"
        IBM01140 = "IBM01140"
        IBM01141 = "IBM01141"
        IBM01142 = "IBM01142"
        IBM01143 = "IBM01143"
        IBM01144 = "IBM01144"
        IBM01145 = "IBM01145"
        IBM01146 = "IBM01146"
        IBM01147 = "IBM01147"
        IBM01148 = "IBM01148"
        IBM01149 = "IBM01149"
        IBM037 = "IBM037"
        IBM1026 = "IBM1026"
        IBM1047 = "IBM1047"
        IBM273 = "IBM273"
        IBM277 = "IBM277"
        IBM278 = "IBM278"
        IBM280 = "IBM280"
        IBM284 = "IBM284"
        IBM285 = "IBM285"
        IBM290 = "IBM290"
        IBM297 = "IBM297"
        IBM420 = "IBM420"
        IBM424 = "IBM424"
        IBM437 = "IBM437"
        IBM500 = "IBM500"
        IBM775 = "IBM775"
        IBM850 = "IBM850"
        IBM851 = "IBM851"
        IBM852 = "IBM852"
        IBM855 = "IBM855"
        IBM857 = "IBM857"
        IBM860 = "IBM860"
        IBM861 = "IBM861"
        IBM862 = "IBM862"
        IBM863 = "IBM863"
        IBM864 = "IBM864"
        IBM865 = "IBM865"
        IBM866 = "IBM866"
        IBM868 = "IBM868"
        IBM869 = "IBM869"
        IBM870 = "IBM870"
        IBM871 = "IBM871"
        IBM918 = "IBM918"
        IMAP_mailbox_name = "IMAP-mailbox-name"
        ISCII_version_0 = "ISCII,version=0"
        ISCII_version_1 = "ISCII,version=1"
        ISCII_version_2 = "ISCII,version=2"
        ISCII_version_3 = "ISCII,version=3"
        ISCII_version_4 = "ISCII,version=4"
        ISCII_version_5 = "ISCII,version=5"
        ISCII_version_6 = "ISCII,version=6"
        ISCII_version_7 = "ISCII,version=7"
        ISCII_version_8 = "ISCII,version=8"
        ISO_2022_locale_ja_version_0 = "ISO_2022,locale=ja,version=0"
        ISO_2022_locale_ja_version_1 = "ISO_2022,locale=ja,version=1"
        ISO_2022_locale_ja_version_2 = "ISO_2022,locale=ja,version=2"
        ISO_2022_locale_ja_version_3 = "ISO_2022,locale=ja,version=3"
        ISO_2022_locale_ja_version_4 = "ISO_2022,locale=ja,version=4"
        ISO_2022_locale_ko_version_0 = "ISO_2022,locale=ko,version=0"
        ISO_2022_locale_ko_version_1 = "ISO_2022,locale=ko,version=1"
        ISO_2022_locale_zh_version_0 = "ISO_2022,locale=zh,version=0"
        ISO_2022_locale_zh_version_1 = "ISO_2022,locale=zh,version=1"
        ISO_2022_locale_zh_version_2 = "ISO_2022,locale=zh,version=2"
        ISO_8859_1_1987 = "ISO_8859-1:1987"
        ISO_8859_2_1987 = "ISO_8859-2:1987"
        ISO_8859_3_1988 = "ISO_8859-3:1988"
        ISO_8859_4_1988 = "ISO_8859-4:1988"
        ISO_8859_5_1988 = "ISO_8859-5:1988"
        ISO_8859_6_1987 = "ISO_8859-6:1987"
        ISO_8859_7_1987 = "ISO_8859-7:1987"
        ISO_8859_8_1988 = "ISO_8859-8:1988"
        ISO_8859_9_1989 = "ISO_8859-9:1989"
        ISO_2022_CN = "ISO-2022-CN"
        ISO_2022_CN_EXT = "ISO-2022-CN-EXT"
        ISO_2022_JP = "ISO-2022-JP"
        ISO_2022_JP_2 = "ISO-2022-JP-2"
        ISO_2022_KR = "ISO-2022-KR"
        iso_8859_10_1998 = "iso-8859_10-1998"
        iso_8859_11_2001 = "iso-8859_11-2001"
        iso_8859_14_1998 = "iso-8859_14-1998"
        ISO_8859_1 = "ISO-8859-1"
        ISO_8859_10 = "ISO-8859-10"
        ISO_8859_13 = "ISO-8859-13"
        ISO_8859_14 = "ISO-8859-14"
        ISO_8859_15 = "ISO-8859-15"
        JIS_Encoding = "JIS_Encoding"
        KOI8_R = "KOI8-R"
        KOI8_U = "KOI8-U"
        KS_C_5601_1987 = "KS_C_5601-1987"
        LMBCS_1 = "LMBCS-1"
        macintosh = "macintosh"
        macos_0_2_10_2 = "macos-0_2-10.2"
        macos_2566_10_2 = "macos-2566-10.2"
        macos_29_10_2 = "macos-29-10.2"
        macos_35_10_2 = "macos-35-10.2"
        macos_6_2_10_4 = "macos-6_2-10.4"
        macos_6_10_2 = "macos-6-10.2"
        macos_7_3_10_2 = "macos-7_3-10.2"
        SCSU = "SCSU"
        Shift_JIS = "Shift_JIS"
        TIS_620 = "TIS-620"
        US_ASCII = "US-ASCII"
        UTF_16 = "UTF-16"
        UTF_16_version_1 = "UTF-16,version=1"
        UTF_16_version_2 = "UTF-16,version=2"
        UTF_16BE = "UTF-16BE"
        UTF_16BE_version_1 = "UTF-16BE,version=1"
        UTF_16LE = "UTF-16LE"
        UTF_16LE_version_1 = "UTF-16LE,version=1"
        UTF_32 = "UTF-32"
        UTF_32BE = "UTF-32BE"
        UTF_32LE = "UTF-32LE"
        UTF_7 = "UTF-7"
        UTF_8 = "UTF-8"
        UTF16_OppositeEndian = "UTF16_OppositeEndian"
        UTF16_PlatformEndian = "UTF16_PlatformEndian"
        UTF32_OppositeEndian = "UTF32_OppositeEndian"
        UTF32_PlatformEndian = "UTF32_PlatformEndian"
        windows_1250 = "windows-1250"
        windows_1251 = "windows-1251"
        windows_1252 = "windows-1252"
        windows_1253 = "windows-1253"
        windows_1254 = "windows-1254"
        windows_1255 = "windows-1255"
        windows_1256 = "windows-1256"
        windows_1256_2000 = "windows-1256-2000"
        windows_1257 = "windows-1257"
        windows_1258 = "windows-1258"
        windows_874_2000 = "windows-874-2000"
        windows_936_2000 = "windows-936-2000"
        windows_949_2000 = "windows-949-2000"
        windows_950_2000 = "windows-950-2000"
        x11_compound_text = "x11-compound-text"

    class AllowColumnMapping(Enum):
        """Enum for the AllowColumnMapping property."""

        false = "False"
        true = "True"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class SPLIT_SUBRECORD:
    """Enums for properties in the SPLIT_SUBRECORD stage."""

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class PEEK:
    """Enums for properties in the PEEK stage."""

    class All(Enum):
        """Enum for the All property."""

        true = "all"
        false = " "

    class Dataset(Enum):
        """Enum for the Dataset property."""

        true = "dataset"
        false = " "

    class Name(Enum):
        """Enum for the Name property."""

        true = "name"
        false = " "

    class Columns(Enum):
        """Enum for the Columns property."""

        true = " "
        false = "field"

    class Selection(Enum):
        """Enum for the Selection property."""

        true = " "
        false = "part"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class EXTERNAL_TARGET:
    """Enums for properties in the EXTERNAL_TARGET stage."""

    class Rejects(Enum):
        """Enum for the Rejects property."""

        save = "save"
        cont = "continue"
        fail = "fail"

    class Selection(Enum):
        """Enum for the Selection property."""

        file = "file"
        program = "program"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class NlsMapName(Enum):
        """Enum for the NlsMapName property."""

        Adobe_Standard_Encoding = "Adobe-Standard-Encoding"
        ANSI_X3_4_1968 = "ANSI_X3.4-1968"
        ASCL_ASCII = "ASCL_ASCII"
        ASCL_ASCII_PC1 = "ASCL_ASCII-PC1"
        ASCL_BIG5 = "ASCL_BIG5"
        ASCL_C0_CONTROLS = "ASCL_C0-CONTROLS"
        ASCL_C1_CONTROLS = "ASCL_C1-CONTROLS"
        ASCL_EBCDIC = "ASCL_EBCDIC"
        ASCL_EBCDIC_037 = "ASCL_EBCDIC-037"
        ASCL_EBCDIC_1026 = "ASCL_EBCDIC-1026"
        ASCL_EBCDIC_500V1 = "ASCL_EBCDIC-500V1"
        ASCL_EBCDIC_875 = "ASCL_EBCDIC-875"
        ASCL_EBCDIC_CTRLS = "ASCL_EBCDIC-CTRLS"
        ASCL_EBCDIC_IBM1364 = "ASCL_EBCDIC-IBM1364"
        ASCL_EBCDIC_IBM1371 = "ASCL_EBCDIC-IBM1371"
        ASCL_EBCDIC_IBM933 = "ASCL_EBCDIC-IBM933"
        ASCL_EBCDIC_IBM937 = "ASCL_EBCDIC-IBM937"
        ASCL_EBCDIC_JP_CTRLS = "ASCL_EBCDIC-JP-CTRLS"
        ASCL_EBCDIC_JP_KANA = "ASCL_EBCDIC-JP-KANA"
        ASCL_EBCDIC_JP_KANA_E = "ASCL_EBCDIC-JP-KANA-E"
        ASCL_EBCDIC_JP_KANA_HW = "ASCL_EBCDIC-JP-KANA-HW"
        ASCL_GB2312 = "ASCL_GB2312"
        ASCL_ISO8859_1 = "ASCL_ISO8859-1"
        ASCL_ISO8859_10 = "ASCL_ISO8859-10"
        ASCL_ISO8859_15 = "ASCL_ISO8859-15"
        ASCL_ISO8859_2 = "ASCL_ISO8859-2"
        ASCL_ISO8859_3 = "ASCL_ISO8859-3"
        ASCL_ISO8859_4 = "ASCL_ISO8859-4"
        ASCL_ISO8859_5 = "ASCL_ISO8859-5"
        ASCL_ISO8859_6 = "ASCL_ISO8859-6"
        ASCL_ISO8859_7 = "ASCL_ISO8859-7"
        ASCL_ISO8859_8 = "ASCL_ISO8859-8"
        ASCL_ISO8859_9 = "ASCL_ISO8859-9"
        ASCL_JIS_EUC = "ASCL_JIS-EUC"
        ASCL_JIS_EUC_HWK = "ASCL_JIS-EUC-HWK"
        ASCL_JIS_EUC_P = "ASCL_JIS-EUC-P"
        ASCL_JIS_ROMAN = "ASCL_JIS-ROMAN"
        ASCL_JISX0201 = "ASCL_JISX0201"
        ASCL_JPN_EBCDIC = "ASCL_JPN-EBCDIC"
        ASCL_JPN_EBCDIK = "ASCL_JPN-EBCDIK"
        ASCL_JPN_EBCDIKC_CTRL = "ASCL_JPN-EBCDIKC-CTRL"
        ASCL_JPN_EUC = "ASCL_JPN-EUC"
        ASCL_JPN_EUC_KAT = "ASCL_JPN-EUC-KAT"
        ASCL_JPN_EUC_ONE = "ASCL_JPN-EUC-ONE"
        ASCL_JPN_EUC_RTE = "ASCL_JPN-EUC-RTE"
        ASCL_JPN_EUC_TWO = "ASCL_JPN-EUC-TWO"
        ASCL_JPN_IBM78 = "ASCL_JPN-IBM78"
        ASCL_JPN_IBM83 = "ASCL_JPN-IBM83"
        ASCL_JPN_JEF78 = "ASCL_JPN-JEF78"
        ASCL_JPN_JEF83 = "ASCL_JPN-JEF83"
        ASCL_JPN_JIPSE = "ASCL_JPN-JIPSE"
        ASCL_JPN_JIPSJ = "ASCL_JPN-JIPSJ"
        ASCL_JPN_JIS_RTE = "ASCL_JPN-JIS-RTE"
        ASCL_JPN_JIS8 = "ASCL_JPN-JIS8"
        ASCL_JPN_JIS8EUC_CTRL = "ASCL_JPN-JIS8EUC-CTRL"
        ASCL_JPN_KEIS_RTE = "ASCL_JPN-KEIS-RTE"
        ASCL_JPN_KEIS78 = "ASCL_JPN-KEIS78"
        ASCL_JPN_KEIS83 = "ASCL_JPN-KEIS83"
        ASCL_JPN_NEBCDIK = "ASCL_JPN-NEBCDIK"
        ASCL_JPN_SJIS = "ASCL_JPN-SJIS"
        ASCL_KOI8_R = "ASCL_KOI8-R"
        ASCL_KSC5601 = "ASCL_KSC5601"
        ASCL_KSC5601_1992 = "ASCL_KSC5601-1992"
        ASCL_MAC_GREEK = "ASCL_MAC-GREEK"
        ASCL_MAC_GREEK2 = "ASCL_MAC-GREEK2"
        ASCL_MAC_ROMAN = "ASCL_MAC-ROMAN"
        ASCL_MNEMONICS = "ASCL_MNEMONICS"
        ASCL_MS1250 = "ASCL_MS1250"
        ASCL_MS1251 = "ASCL_MS1251"
        ASCL_MS1252 = "ASCL_MS1252"
        ASCL_MS1253 = "ASCL_MS1253"
        ASCL_MS1254 = "ASCL_MS1254"
        ASCL_MS1255 = "ASCL_MS1255"
        ASCL_MS1256 = "ASCL_MS1256"
        ASCL_MS932 = "ASCL_MS932"
        ASCL_MS932_BASE = "ASCL_MS932-BASE"
        ASCL_MS932_EXTRA = "ASCL_MS932-EXTRA"
        ASCL_MS936 = "ASCL_MS936"
        ASCL_MS936_BASE = "ASCL_MS936-BASE"
        ASCL_MS949 = "ASCL_MS949"
        ASCL_MS950 = "ASCL_MS950"
        ASCL_MS950_BASE = "ASCL_MS950-BASE"
        ASCL_PC1040 = "ASCL_PC1040"
        ASCL_PC1041 = "ASCL_PC1041"
        ASCL_PC437 = "ASCL_PC437"
        ASCL_PC850 = "ASCL_PC850"
        ASCL_PC852 = "ASCL_PC852"
        ASCL_PC855 = "ASCL_PC855"
        ASCL_PC857 = "ASCL_PC857"
        ASCL_PC860 = "ASCL_PC860"
        ASCL_PC861 = "ASCL_PC861"
        ASCL_PC862 = "ASCL_PC862"
        ASCL_PC863 = "ASCL_PC863"
        ASCL_PC864 = "ASCL_PC864"
        ASCL_PC865 = "ASCL_PC865"
        ASCL_PC866 = "ASCL_PC866"
        ASCL_PC869 = "ASCL_PC869"
        ASCL_PC874 = "ASCL_PC874"
        ASCL_PRIME_SHIFT_JIS = "ASCL_PRIME-SHIFT-JIS"
        ASCL_SHIFT_JIS = "ASCL_SHIFT-JIS"
        ASCL_TAU_SHIFT_JIS = "ASCL_TAU-SHIFT-JIS"
        ASCL_TIS620 = "ASCL_TIS620"
        ASCL_TIS620_B = "ASCL_TIS620-B"
        Big5 = "Big5"
        Big5_HKSCS = "Big5-HKSCS"
        BOCU_1 = "BOCU-1"
        CESU_8 = "CESU-8"
        ebcdic_xml_us = "ebcdic-xml-us"
        EUC_KR = "EUC-KR"
        GB_2312_80 = "GB_2312-80"
        gb18030_gb18030 = "gb18030 gb18030"
        GB2312 = "GB2312"
        GBK = "GBK"
        hp_roman8 = "hp-roman8"
        HZ_HZ_GB_2312 = "HZ HZ-GB-2312"
        ibm_1006_P100_1995 = "ibm-1006_P100-1995"
        ibm_1025_P100_1995 = "ibm-1025_P100-1995"
        ibm_1026_P100_1995 = "ibm-1026_P100-1995"
        ibm_1047_P100_1995 = "ibm-1047_P100-1995"
        ibm_1047_P100_1995_swaplfnl = "ibm-1047_P100-1995,swaplfnl"
        ibm_1051_P100_1995 = "ibm-1051_P100-1995"
        ibm_1089_P100_1995 = "ibm-1089_P100-1995"
        ibm_1097_P100_1995 = "ibm-1097_P100-1995"
        ibm_1098_P100_1995 = "ibm-1098_P100-1995"
        ibm_1112_P100_1995 = "ibm-1112_P100-1995"
        ibm_1122_P100_1999 = "ibm-1122_P100-1999"
        ibm_1123_P100_1995 = "ibm-1123_P100-1995"
        ibm_1124_P100_1996 = "ibm-1124_P100-1996"
        ibm_1125_P100_1997 = "ibm-1125_P100-1997"
        ibm_1129_P100_1997 = "ibm-1129_P100-1997"
        ibm_1130_P100_1997 = "ibm-1130_P100-1997"
        ibm_1131_P100_1997 = "ibm-1131_P100-1997"
        ibm_1132_P100_1998 = "ibm-1132_P100-1998"
        ibm_1133_P100_1997 = "ibm-1133_P100-1997"
        ibm_1137_P100_1999 = "ibm-1137_P100-1999"
        ibm_1140_P100_1997 = "ibm-1140_P100-1997"
        ibm_1140_P100_1997_swaplfnl = "ibm-1140_P100-1997,swaplfnl"
        ibm_1141_P100_1997 = "ibm-1141_P100-1997"
        ibm_1141_P100_1997_swaplfnl = "ibm-1141_P100-1997,swaplfnl"
        ibm_1142_P100_1997 = "ibm-1142_P100-1997"
        ibm_1142_P100_1997_swaplfnl = "ibm-1142_P100-1997,swaplfnl"
        ibm_1143_P100_1997 = "ibm-1143_P100-1997"
        ibm_1143_P100_1997_swaplfnl = "ibm-1143_P100-1997,swaplfnl"
        ibm_1144_P100_1997 = "ibm-1144_P100-1997"
        ibm_1144_P100_1997_swaplfnl = "ibm-1144_P100-1997,swaplfnl"
        ibm_1145_P100_1997 = "ibm-1145_P100-1997"
        ibm_1145_P100_1997_swaplfnl = "ibm-1145_P100-1997,swaplfnl"
        ibm_1146_P100_1997 = "ibm-1146_P100-1997"
        ibm_1146_P100_1997_swaplfnl = "ibm-1146_P100-1997,swaplfnl"
        ibm_1147_P100_1997 = "ibm-1147_P100-1997"
        ibm_1147_P100_1997_swaplfnl = "ibm-1147_P100-1997,swaplfnl"
        ibm_1148_P100_1997 = "ibm-1148_P100-1997"
        ibm_1148_P100_1997_swaplfnl = "ibm-1148_P100-1997,swaplfnl"
        ibm_1149_P100_1997 = "ibm-1149_P100-1997"
        ibm_1149_P100_1997_swaplfnl = "ibm-1149_P100-1997,swaplfnl"
        ibm_1153_P100_1999 = "ibm-1153_P100-1999"
        ibm_1153_P100_1999_swaplfnl = "ibm-1153_P100-1999,swaplfnl"
        ibm_1154_P100_1999 = "ibm-1154_P100-1999"
        ibm_1155_P100_1999 = "ibm-1155_P100-1999"
        ibm_1156_P100_1999 = "ibm-1156_P100-1999"
        ibm_1157_P100_1999 = "ibm-1157_P100-1999"
        ibm_1158_P100_1999 = "ibm-1158_P100-1999"
        ibm_1160_P100_1999 = "ibm-1160_P100-1999"
        ibm_1162_P100_1999 = "ibm-1162_P100-1999"
        ibm_1164_P100_1999 = "ibm-1164_P100-1999"
        ibm_1168_P100_2002 = "ibm-1168_P100-2002"
        ibm_1250_P100_1995 = "ibm-1250_P100-1995"
        ibm_1251_P100_1995 = "ibm-1251_P100-1995"
        ibm_1252_P100_2000 = "ibm-1252_P100-2000"
        ibm_1253_P100_1995 = "ibm-1253_P100-1995"
        ibm_1254_P100_1995 = "ibm-1254_P100-1995"
        ibm_1255_P100_1995 = "ibm-1255_P100-1995"
        ibm_1256_P110_1997 = "ibm-1256_P110-1997"
        ibm_1257_P100_1995 = "ibm-1257_P100-1995"
        ibm_1258_P100_1997 = "ibm-1258_P100-1997"
        ibm_12712_P100_1998 = "ibm-12712_P100-1998"
        ibm_12712_P100_1998_swaplfnl = "ibm-12712_P100-1998,swaplfnl"
        ibm_1276_P100_1995 = "ibm-1276_P100-1995"
        ibm_1277_P100_1995 = "ibm-1277_P100-1995"
        ibm_1363_P110_1997 = "ibm-1363_P110-1997"
        ibm_1363_P11B_1998 = "ibm-1363_P11B-1998"
        ibm_1364_P110_1997 = "ibm-1364_P110-1997"
        ibm_1364_P110_2007 = "ibm-1364_P110-2007"
        ibm_1371_P100_1999 = "ibm-1371_P100-1999"
        ibm_1373_P100_2002 = "ibm-1373_P100-2002"
        ibm_1375_P100_2003 = "ibm-1375_P100-2003"
        ibm_1375_P100_2007 = "ibm-1375_P100-2007"
        ibm_1381_P110_1999 = "ibm-1381_P110-1999"
        ibm_1383_P110_1999 = "ibm-1383_P110-1999"
        ibm_1386_P100_2001 = "ibm-1386_P100-2001"
        ibm_1386_P100_2002 = "ibm-1386_P100-2002"
        ibm_1388_P103_2001 = "ibm-1388_P103-2001"
        ibm_1390_P110_2003 = "ibm-1390_P110-2003"
        ibm_1399_P110_2003 = "ibm-1399_P110-2003"
        ibm_16684_P110_2003 = "ibm-16684_P110-2003"
        ibm_16804_X110_1999 = "ibm-16804_X110-1999"
        ibm_16804_X110_1999_swaplfnl = "ibm-16804_X110-1999,swaplfnl"
        ibm_273_P100_1995 = "ibm-273_P100-1995"
        ibm_277_P100_1995 = "ibm-277_P100-1995"
        ibm_278_P100_1995 = "ibm-278_P100-1995"
        ibm_280_P100_1995 = "ibm-280_P100-1995"
        ibm_284_P100_1995 = "ibm-284_P100-1995"
        ibm_285_P100_1995 = "ibm-285_P100-1995"
        ibm_290_P100_1995 = "ibm-290_P100-1995"
        ibm_297_P100_1995 = "ibm-297_P100-1995"
        ibm_33722_P120_1999 = "ibm-33722_P120-1999"
        ibm_33722_P12A_P12A_2009_U2_Extended_UNIX_Code_Packed_Format_for_Japanese = (
            "ibm-33722_P12A_P12A-2009_U2 Extended_UNIX_Code_Packed_Format_for_Japanese"
        )
        ibm_33722_P12A_1999 = "ibm-33722_P12A-1999"
        ibm_367_P100_1995 = "ibm-367_P100-1995"
        ibm_37_P100_1995 = "ibm-37_P100-1995"
        ibm_37_P100_1995_swaplfnl = "ibm-37_P100-1995,swaplfnl"
        ibm_420_X120_1999 = "ibm-420_X120-1999"
        ibm_424_P100_1995 = "ibm-424_P100-1995"
        ibm_437_P100_1995 = "ibm-437_P100-1995"
        ibm_4517_P100_2005 = "ibm-4517_P100-2005"
        ibm_4899_P100_1998 = "ibm-4899_P100-1998"
        ibm_4909_P100_1999 = "ibm-4909_P100-1999"
        ibm_4971_P100_1999 = "ibm-4971_P100-1999"
        ibm_500_P100_1995 = "ibm-500_P100-1995"
        ibm_5012_P100_1999 = "ibm-5012_P100-1999"
        ibm_5123_P100_1999 = "ibm-5123_P100-1999"
        ibm_5346_P100_1998 = "ibm-5346_P100-1998"
        ibm_5347_P100_1998 = "ibm-5347_P100-1998"
        ibm_5348_P100_1997 = "ibm-5348_P100-1997"
        ibm_5349_P100_1998 = "ibm-5349_P100-1998"
        ibm_5350_P100_1998 = "ibm-5350_P100-1998"
        ibm_5351_P100_1998 = "ibm-5351_P100-1998"
        ibm_5352_P100_1998 = "ibm-5352_P100-1998"
        ibm_5353_P100_1998 = "ibm-5353_P100-1998"
        ibm_5354_P100_1998 = "ibm-5354_P100-1998"
        ibm_5471_P100_2006 = "ibm-5471_P100-2006"
        ibm_5478_P100_1995 = "ibm-5478_P100-1995"
        ibm_720_P100_1997 = "ibm-720_P100-1997"
        ibm_737_P100_1997 = "ibm-737_P100-1997"
        ibm_775_P100_1996 = "ibm-775_P100-1996"
        ibm_803_P100_1999 = "ibm-803_P100-1999"
        ibm_813_P100_1995 = "ibm-813_P100-1995"
        ibm_838_P100_1995 = "ibm-838_P100-1995"
        ibm_8482_P100_1999 = "ibm-8482_P100-1999"
        ibm_850_P100_1995 = "ibm-850_P100-1995"
        ibm_851_P100_1995 = "ibm-851_P100-1995"
        ibm_852_P100_1995 = "ibm-852_P100-1995"
        ibm_855_P100_1995 = "ibm-855_P100-1995"
        ibm_856_P100_1995 = "ibm-856_P100-1995"
        ibm_857_P100_1995 = "ibm-857_P100-1995"
        ibm_858_P100_1997 = "ibm-858_P100-1997"
        ibm_860_P100_1995 = "ibm-860_P100-1995"
        ibm_861_P100_1995 = "ibm-861_P100-1995"
        ibm_862_P100_1995 = "ibm-862_P100-1995"
        ibm_863_P100_1995 = "ibm-863_P100-1995"
        ibm_864_X110_1999 = "ibm-864_X110-1999"
        ibm_865_P100_1995 = "ibm-865_P100-1995"
        ibm_866_P100_1995 = "ibm-866_P100-1995"
        ibm_867_P100_1998 = "ibm-867_P100-1998"
        ibm_868_P100_1995 = "ibm-868_P100-1995"
        ibm_869_P100_1995 = "ibm-869_P100-1995"
        ibm_870_P100_1995 = "ibm-870_P100-1995"
        ibm_871_P100_1995 = "ibm-871_P100-1995"
        ibm_874_P100_1995 = "ibm-874_P100-1995"
        ibm_875_P100_1995 = "ibm-875_P100-1995"
        ibm_878_P100_1996 = "ibm-878_P100-1996"
        ibm_897_P100_1995 = "ibm-897_P100-1995"
        ibm_9005_X110_2007 = "ibm-9005_X110-2007"
        ibm_901_P100_1999 = "ibm-901_P100-1999"
        ibm_902_P100_1999 = "ibm-902_P100-1999"
        ibm_9067_X100_2005 = "ibm-9067_X100-2005"
        ibm_912_P100_1995 = "ibm-912_P100-1995"
        ibm_913_P100_2000 = "ibm-913_P100-2000"
        ibm_914_P100_1995 = "ibm-914_P100-1995"
        ibm_915_P100_1995 = "ibm-915_P100-1995"
        ibm_916_P100_1995 = "ibm-916_P100-1995"
        ibm_918_P100_1995 = "ibm-918_P100-1995"
        ibm_920_P100_1995 = "ibm-920_P100-1995"
        ibm_921_P100_1995 = "ibm-921_P100-1995"
        ibm_922_P100_1999 = "ibm-922_P100-1999"
        ibm_923_P100_1998 = "ibm-923_P100-1998"
        ibm_930_P120_1999 = "ibm-930_P120-1999"
        ibm_933_P110_1995 = "ibm-933_P110-1995"
        ibm_935_P110_1999 = "ibm-935_P110-1999"
        ibm_937_P110_1999 = "ibm-937_P110-1999"
        ibm_939_P120_1999 = "ibm-939_P120-1999"
        ibm_942_P12A_1999 = "ibm-942_P12A-1999"
        ibm_943_P130_1999 = "ibm-943_P130-1999"
        ibm_943_P15A_2003 = "ibm-943_P15A-2003"
        ibm_9447_P100_2002 = "ibm-9447_P100-2002"
        ibm_9448_X100_2005 = "ibm-9448_X100-2005"
        ibm_9449_P100_2002 = "ibm-9449_P100-2002"
        ibm_949_P110_1999 = "ibm-949_P110-1999"
        ibm_949_P11A_1999 = "ibm-949_P11A-1999"
        ibm_950_P110_1999 = "ibm-950_P110-1999"
        ibm_954_P101_2000 = "ibm-954_P101-2000"
        ibm_954_P101_2007 = "ibm-954_P101-2007"
        ibm_964_P110_1999 = "ibm-964_P110-1999"
        ibm_970_P110_P110_2006_U2 = "ibm-970_P110_P110-2006_U2"
        ibm_970_P110_1995 = "ibm-970_P110-1995"
        ibm_971_P100_1995 = "ibm-971_P100-1995"
        IBM_Thai = "IBM-Thai"
        IBM00858 = "IBM00858"
        IBM01140 = "IBM01140"
        IBM01141 = "IBM01141"
        IBM01142 = "IBM01142"
        IBM01143 = "IBM01143"
        IBM01144 = "IBM01144"
        IBM01145 = "IBM01145"
        IBM01146 = "IBM01146"
        IBM01147 = "IBM01147"
        IBM01148 = "IBM01148"
        IBM01149 = "IBM01149"
        IBM037 = "IBM037"
        IBM1026 = "IBM1026"
        IBM1047 = "IBM1047"
        IBM273 = "IBM273"
        IBM277 = "IBM277"
        IBM278 = "IBM278"
        IBM280 = "IBM280"
        IBM284 = "IBM284"
        IBM285 = "IBM285"
        IBM290 = "IBM290"
        IBM297 = "IBM297"
        IBM420 = "IBM420"
        IBM424 = "IBM424"
        IBM437 = "IBM437"
        IBM500 = "IBM500"
        IBM775 = "IBM775"
        IBM850 = "IBM850"
        IBM851 = "IBM851"
        IBM852 = "IBM852"
        IBM855 = "IBM855"
        IBM857 = "IBM857"
        IBM860 = "IBM860"
        IBM861 = "IBM861"
        IBM862 = "IBM862"
        IBM863 = "IBM863"
        IBM864 = "IBM864"
        IBM865 = "IBM865"
        IBM866 = "IBM866"
        IBM868 = "IBM868"
        IBM869 = "IBM869"
        IBM870 = "IBM870"
        IBM871 = "IBM871"
        IBM918 = "IBM918"
        IMAP_mailbox_name = "IMAP-mailbox-name"
        ISCII_version_0 = "ISCII,version=0"
        ISCII_version_1 = "ISCII,version=1"
        ISCII_version_2 = "ISCII,version=2"
        ISCII_version_3 = "ISCII,version=3"
        ISCII_version_4 = "ISCII,version=4"
        ISCII_version_5 = "ISCII,version=5"
        ISCII_version_6 = "ISCII,version=6"
        ISCII_version_7 = "ISCII,version=7"
        ISCII_version_8 = "ISCII,version=8"
        ISO_2022_locale_ja_version_0 = "ISO_2022,locale=ja,version=0"
        ISO_2022_locale_ja_version_1 = "ISO_2022,locale=ja,version=1"
        ISO_2022_locale_ja_version_2 = "ISO_2022,locale=ja,version=2"
        ISO_2022_locale_ja_version_3 = "ISO_2022,locale=ja,version=3"
        ISO_2022_locale_ja_version_4 = "ISO_2022,locale=ja,version=4"
        ISO_2022_locale_ko_version_0 = "ISO_2022,locale=ko,version=0"
        ISO_2022_locale_ko_version_1 = "ISO_2022,locale=ko,version=1"
        ISO_2022_locale_zh_version_0 = "ISO_2022,locale=zh,version=0"
        ISO_2022_locale_zh_version_1 = "ISO_2022,locale=zh,version=1"
        ISO_2022_locale_zh_version_2 = "ISO_2022,locale=zh,version=2"
        ISO_8859_1_1987 = "ISO_8859-1:1987"
        ISO_8859_2_1987 = "ISO_8859-2:1987"
        ISO_8859_3_1988 = "ISO_8859-3:1988"
        ISO_8859_4_1988 = "ISO_8859-4:1988"
        ISO_8859_5_1988 = "ISO_8859-5:1988"
        ISO_8859_6_1987 = "ISO_8859-6:1987"
        ISO_8859_7_1987 = "ISO_8859-7:1987"
        ISO_8859_8_1988 = "ISO_8859-8:1988"
        ISO_8859_9_1989 = "ISO_8859-9:1989"
        ISO_2022_CN = "ISO-2022-CN"
        ISO_2022_CN_EXT = "ISO-2022-CN-EXT"
        ISO_2022_JP = "ISO-2022-JP"
        ISO_2022_JP_2 = "ISO-2022-JP-2"
        ISO_2022_KR = "ISO-2022-KR"
        iso_8859_10_1998 = "iso-8859_10-1998"
        iso_8859_11_2001 = "iso-8859_11-2001"
        iso_8859_14_1998 = "iso-8859_14-1998"
        ISO_8859_1 = "ISO-8859-1"
        ISO_8859_10 = "ISO-8859-10"
        ISO_8859_13 = "ISO-8859-13"
        ISO_8859_14 = "ISO-8859-14"
        ISO_8859_15 = "ISO-8859-15"
        JIS_Encoding = "JIS_Encoding"
        KOI8_R = "KOI8-R"
        KOI8_U = "KOI8-U"
        KS_C_5601_1987 = "KS_C_5601-1987"
        LMBCS_1 = "LMBCS-1"
        macintosh = "macintosh"
        macos_0_2_10_2 = "macos-0_2-10.2"
        macos_2566_10_2 = "macos-2566-10.2"
        macos_29_10_2 = "macos-29-10.2"
        macos_35_10_2 = "macos-35-10.2"
        macos_6_2_10_4 = "macos-6_2-10.4"
        macos_6_10_2 = "macos-6-10.2"
        macos_7_3_10_2 = "macos-7_3-10.2"
        SCSU = "SCSU"
        Shift_JIS = "Shift_JIS"
        TIS_620 = "TIS-620"
        US_ASCII = "US-ASCII"
        UTF_16 = "UTF-16"
        UTF_16_version_1 = "UTF-16,version=1"
        UTF_16_version_2 = "UTF-16,version=2"
        UTF_16BE = "UTF-16BE"
        UTF_16BE_version_1 = "UTF-16BE,version=1"
        UTF_16LE = "UTF-16LE"
        UTF_16LE_version_1 = "UTF-16LE,version=1"
        UTF_32 = "UTF-32"
        UTF_32BE = "UTF-32BE"
        UTF_32LE = "UTF-32LE"
        UTF_7 = "UTF-7"
        UTF_8 = "UTF-8"
        UTF16_OppositeEndian = "UTF16_OppositeEndian"
        UTF16_PlatformEndian = "UTF16_PlatformEndian"
        UTF32_OppositeEndian = "UTF32_OppositeEndian"
        UTF32_PlatformEndian = "UTF32_PlatformEndian"
        windows_1250 = "windows-1250"
        windows_1251 = "windows-1251"
        windows_1252 = "windows-1252"
        windows_1253 = "windows-1253"
        windows_1254 = "windows-1254"
        windows_1255 = "windows-1255"
        windows_1256 = "windows-1256"
        windows_1256_2000 = "windows-1256-2000"
        windows_1257 = "windows-1257"
        windows_1258 = "windows-1258"
        windows_874_2000 = "windows-874-2000"
        windows_936_2000 = "windows-936-2000"
        windows_949_2000 = "windows-949-2000"
        windows_950_2000 = "windows-950-2000"
        x11_compound_text = "x11-compound-text"

    class AllowColumnMapping(Enum):
        """Enum for the AllowColumnMapping property."""

        false = "False"
        true = "True"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class FinalDelim(Enum):
        """Enum for the FinalDelim property."""

        custom = " "
        ws = "ws"
        end = "end"
        none = "none"
        null = "null"
        comma = "','"
        tab = "'\t'"

    class Fill(Enum):
        """Enum for the Fill property."""

        custom_fill_char = -1
        null = 0

    class CheckIntact(Enum):
        """Enum for the CheckIntact property."""

        check_intact = "check_intact"

    class RecordDelim(Enum):
        """Enum for the RecordDelim property."""

        custom = " "
        newline = "'\n'"
        null = "null"

    class RecordPrefix(Enum):
        """Enum for the RecordPrefix property."""

        one = 1
        two = 2
        four = 4

    class RecordLength(Enum):
        """Enum for the RecordLength property."""

        custom = " "
        fixed = "fixed"

    class RecordFormat(Enum):
        """Enum for the RecordFormat property."""

        type_implicit = "{type=implicit}"
        type_varying = "{type=varying}"
        type_varying_format_V = "{type=varying, format=V}"
        type_varying_format_VB = "{type=varying, format=VB}"
        type_varying_format_VBS = "{type=varying, format=VBS}"
        type_varying_format_VR = "{type=varying, format=VR}"
        type_varying_format_VS = "{type=varying, format=VS}"

    class Delim(Enum):
        """Enum for the Delim property."""

        custom = " "
        ws = "ws"
        end = "end"
        none = "none"
        null = "null"
        comma = "','"
        tab = "'\t'"

    class Quote(Enum):
        """Enum for the Quote property."""

        custom = " "
        single = "single"
        double = "double"
        none = "none"

    class NullFieldSep(Enum):
        """Enum for the NullFieldSep property."""

        space = " "
        comma = "','"

    class PrintField(Enum):
        """Enum for the PrintField property."""

        print_field = "print_field"

    class VectorPrefix(Enum):
        """Enum for the VectorPrefix property."""

        one = 1
        two = 2
        four = 4

    class Prefix(Enum):
        """Enum for the Prefix property."""

        one = 1
        two = 2
        four = 4

    class ByteOrder(Enum):
        """Enum for the ByteOrder property."""

        little_endian = "little_endian"
        big_endian = "big_endian"
        native_endian = "native_endian"

    class Charset(Enum):
        """Enum for the Charset property."""

        ebcdic = "ebcdic"
        ascii = "ascii"

    class DataFormat(Enum):
        """Enum for the DataFormat property."""

        binary = "binary"
        text = "text"

    class Padchar(Enum):
        """Enum for the Padchar property."""

        custom = " "
        false_ = "' '"
        null = "null"

    class ExportEbcdicAsAscii(Enum):
        """Enum for the ExportEbcdicAsAscii property."""

        export_ebcdic_as_ascii = "export_ebcdic_as_ascii"

    class ImportAsciiAsEbcdic(Enum):
        """Enum for the ImportAsciiAsEbcdic property."""

        import_ascii_as_ebcdic = "import_ascii_as_ebcdic"

    class AllowAllZeros(Enum):
        """Enum for the AllowAllZeros property."""

        nofix_zero = "nofix_zero"
        fix_zero = "fix_zero"

    class DecimalSeparator(Enum):
        """Enum for the DecimalSeparator property."""

        custom = " "
        comma = "','"
        period = "'.'"

    class DecimalPacked(Enum):
        """Enum for the DecimalPacked property."""

        packed = "packed"
        separate = "separate"
        zoned = "zoned"
        overpunch = "overpunch"

    class DecimalPackedCheck(Enum):
        """Enum for the DecimalPackedCheck property."""

        check = "check"
        nocheck = "nocheck"

    class DecimalPackedSigned(Enum):
        """Enum for the DecimalPackedSigned property."""

        signed = "signed"
        unsigned = "unsigned"

    class AllowSignedImport(Enum):
        """Enum for the AllowSignedImport property."""

        allow_signed_import = "allow_signed_import"

    class DecimalPackedSignPosition(Enum):
        """Enum for the DecimalPackedSignPosition property."""

        trailing = "trailing"
        leading = "leading"

    class Round(Enum):
        """Enum for the Round property."""

        ceil = "ceil"
        floor = "floor"
        round_inf = "round_inf"
        trunc_zero = "trunc_zero"

    class IsJulian(Enum):
        """Enum for the IsJulian property."""

        julian = "julian"

    class IsMidnightSeconds(Enum):
        """Enum for the IsMidnightSeconds property."""

        midnight_seconds = "midnight_seconds"

    class RecLevelOption(Enum):
        """Enum for the RecLevelOption property."""

        final_delimiter = "final_delimiter"
        fill = "fill"
        final_delim_string = "final_delim_string"
        intact = "intact"
        record_delimiter = "record_delimiter"
        record_delim_string = "record_delim_string"
        record_length = "record_length"
        record_prefix = "record_prefix"
        record_format = "record_format"

    class FieldOption(Enum):
        """Enum for the FieldOption property."""

        delimiter = "delimiter"
        quote = "quote"
        actual_length = "actual_length"
        delim_string = "delim_string"
        null_length = "null_length"
        null_field = "null_field"
        prefix_bytes = "prefix_bytes"
        print_field = "print_field"
        vector_prefix = "vector_prefix"

    class GeneralOption(Enum):
        """Enum for the GeneralOption property."""

        byte_order = "byte_order"
        charset = "charset"
        data_format = "data_format"
        max_width = "max_width"
        field_width = "field_width"
        padchar = "padchar"

    class StringOption(Enum):
        """Enum for the StringOption property."""

        export_ebcdic_as_ascii = "export_ebcdic_as_ascii"
        import_ascii_as_ebcdic = "import_ascii_as_ebcdic"

    class DecimalOption(Enum):
        """Enum for the DecimalOption property."""

        allow_all_zeros = "allow_all_zeros"
        decimal_separator = "decimal_separator"
        decimal_packed = "decimal_packed"
        precision = "precision"
        round = "round"
        scale = "scale"

    class NumericOption(Enum):
        """Enum for the NumericOption property."""

        c_format = "c_format"
        in_format = "in_format"
        out_format = "out_format"

    class DateOption(Enum):
        """Enum for the DateOption property."""

        none = "none"
        days_since = "days_since"
        date_format = "date_format"
        is_julian = "is_julian"

    class TimeOption(Enum):
        """Enum for the TimeOption property."""

        none = "none"
        time_format = "time_format"
        is_midnight_seconds = "is_midnight_seconds"

    class TimestampOption(Enum):
        """Enum for the TimestampOption property."""

        none = "none"
        timestamp_format = "timestamp_format"


class EXTERNAL_SOURCE:
    """Enums for properties in the EXTERNAL_SOURCE stage."""

    class KeepPartitions(Enum):
        """Enum for the KeepPartitions property."""

        true = "keepPartitions"
        false = " "

    class RejectMode(Enum):
        """Enum for the RejectMode property."""

        save = "save"
        cont = "continue"
        fail = "fail"

    class SourceMethod(Enum):
        """Enum for the SourceMethod property."""

        file = "file"
        program = "program"

    class StripBom(Enum):
        """Enum for the StripBom property."""

        true = "stripbom"
        false = " "

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_set = -2
        default_clear = -1
        clear = 0
        set = 1

    class MapName(Enum):
        """Enum for the MapName property."""

        Adobe_Standard_Encoding = "Adobe-Standard-Encoding"
        ANSI_X3_4_1968 = "ANSI_X3.4-1968"
        ASCL_ASCII = "ASCL_ASCII"
        ASCL_ASCII_PC1 = "ASCL_ASCII-PC1"
        ASCL_BIG5 = "ASCL_BIG5"
        ASCL_C0_CONTROLS = "ASCL_C0-CONTROLS"
        ASCL_C1_CONTROLS = "ASCL_C1-CONTROLS"
        ASCL_EBCDIC = "ASCL_EBCDIC"
        ASCL_EBCDIC_037 = "ASCL_EBCDIC-037"
        ASCL_EBCDIC_1026 = "ASCL_EBCDIC-1026"
        ASCL_EBCDIC_500V1 = "ASCL_EBCDIC-500V1"
        ASCL_EBCDIC_875 = "ASCL_EBCDIC-875"
        ASCL_EBCDIC_CTRLS = "ASCL_EBCDIC-CTRLS"
        ASCL_EBCDIC_IBM1364 = "ASCL_EBCDIC-IBM1364"
        ASCL_EBCDIC_IBM1371 = "ASCL_EBCDIC-IBM1371"
        ASCL_EBCDIC_IBM933 = "ASCL_EBCDIC-IBM933"
        ASCL_EBCDIC_IBM937 = "ASCL_EBCDIC-IBM937"
        ASCL_EBCDIC_JP_CTRLS = "ASCL_EBCDIC-JP-CTRLS"
        ASCL_EBCDIC_JP_KANA = "ASCL_EBCDIC-JP-KANA"
        ASCL_EBCDIC_JP_KANA_E = "ASCL_EBCDIC-JP-KANA-E"
        ASCL_EBCDIC_JP_KANA_HW = "ASCL_EBCDIC-JP-KANA-HW"
        ASCL_GB2312 = "ASCL_GB2312"
        ASCL_ISO8859_1 = "ASCL_ISO8859-1"
        ASCL_ISO8859_10 = "ASCL_ISO8859-10"
        ASCL_ISO8859_15 = "ASCL_ISO8859-15"
        ASCL_ISO8859_2 = "ASCL_ISO8859-2"
        ASCL_ISO8859_3 = "ASCL_ISO8859-3"
        ASCL_ISO8859_4 = "ASCL_ISO8859-4"
        ASCL_ISO8859_5 = "ASCL_ISO8859-5"
        ASCL_ISO8859_6 = "ASCL_ISO8859-6"
        ASCL_ISO8859_7 = "ASCL_ISO8859-7"
        ASCL_ISO8859_8 = "ASCL_ISO8859-8"
        ASCL_ISO8859_9 = "ASCL_ISO8859-9"
        ASCL_JIS_EUC = "ASCL_JIS-EUC"
        ASCL_JIS_EUC_HWK = "ASCL_JIS-EUC-HWK"
        ASCL_JIS_EUC_P = "ASCL_JIS-EUC-P"
        ASCL_JIS_ROMAN = "ASCL_JIS-ROMAN"
        ASCL_JISX0201 = "ASCL_JISX0201"
        ASCL_JPN_EBCDIC = "ASCL_JPN-EBCDIC"
        ASCL_JPN_EBCDIK = "ASCL_JPN-EBCDIK"
        ASCL_JPN_EBCDIKC_CTRL = "ASCL_JPN-EBCDIKC-CTRL"
        ASCL_JPN_EUC = "ASCL_JPN-EUC"
        ASCL_JPN_EUC_KAT = "ASCL_JPN-EUC-KAT"
        ASCL_JPN_EUC_ONE = "ASCL_JPN-EUC-ONE"
        ASCL_JPN_EUC_RTE = "ASCL_JPN-EUC-RTE"
        ASCL_JPN_EUC_TWO = "ASCL_JPN-EUC-TWO"
        ASCL_JPN_IBM78 = "ASCL_JPN-IBM78"
        ASCL_JPN_IBM83 = "ASCL_JPN-IBM83"
        ASCL_JPN_JEF78 = "ASCL_JPN-JEF78"
        ASCL_JPN_JEF83 = "ASCL_JPN-JEF83"
        ASCL_JPN_JIPSE = "ASCL_JPN-JIPSE"
        ASCL_JPN_JIPSJ = "ASCL_JPN-JIPSJ"
        ASCL_JPN_JIS_RTE = "ASCL_JPN-JIS-RTE"
        ASCL_JPN_JIS8 = "ASCL_JPN-JIS8"
        ASCL_JPN_JIS8EUC_CTRL = "ASCL_JPN-JIS8EUC-CTRL"
        ASCL_JPN_KEIS_RTE = "ASCL_JPN-KEIS-RTE"
        ASCL_JPN_KEIS78 = "ASCL_JPN-KEIS78"
        ASCL_JPN_KEIS83 = "ASCL_JPN-KEIS83"
        ASCL_JPN_NEBCDIK = "ASCL_JPN-NEBCDIK"
        ASCL_JPN_SJIS = "ASCL_JPN-SJIS"
        ASCL_KOI8_R = "ASCL_KOI8-R"
        ASCL_KSC5601 = "ASCL_KSC5601"
        ASCL_KSC5601_1992 = "ASCL_KSC5601-1992"
        ASCL_MAC_GREEK = "ASCL_MAC-GREEK"
        ASCL_MAC_GREEK2 = "ASCL_MAC-GREEK2"
        ASCL_MAC_ROMAN = "ASCL_MAC-ROMAN"
        ASCL_MNEMONICS = "ASCL_MNEMONICS"
        ASCL_MS1250 = "ASCL_MS1250"
        ASCL_MS1251 = "ASCL_MS1251"
        ASCL_MS1252 = "ASCL_MS1252"
        ASCL_MS1253 = "ASCL_MS1253"
        ASCL_MS1254 = "ASCL_MS1254"
        ASCL_MS1255 = "ASCL_MS1255"
        ASCL_MS1256 = "ASCL_MS1256"
        ASCL_MS932 = "ASCL_MS932"
        ASCL_MS932_BASE = "ASCL_MS932-BASE"
        ASCL_MS932_EXTRA = "ASCL_MS932-EXTRA"
        ASCL_MS936 = "ASCL_MS936"
        ASCL_MS936_BASE = "ASCL_MS936-BASE"
        ASCL_MS949 = "ASCL_MS949"
        ASCL_MS950 = "ASCL_MS950"
        ASCL_MS950_BASE = "ASCL_MS950-BASE"
        ASCL_PC1040 = "ASCL_PC1040"
        ASCL_PC1041 = "ASCL_PC1041"
        ASCL_PC437 = "ASCL_PC437"
        ASCL_PC850 = "ASCL_PC850"
        ASCL_PC852 = "ASCL_PC852"
        ASCL_PC855 = "ASCL_PC855"
        ASCL_PC857 = "ASCL_PC857"
        ASCL_PC860 = "ASCL_PC860"
        ASCL_PC861 = "ASCL_PC861"
        ASCL_PC862 = "ASCL_PC862"
        ASCL_PC863 = "ASCL_PC863"
        ASCL_PC864 = "ASCL_PC864"
        ASCL_PC865 = "ASCL_PC865"
        ASCL_PC866 = "ASCL_PC866"
        ASCL_PC869 = "ASCL_PC869"
        ASCL_PC874 = "ASCL_PC874"
        ASCL_PRIME_SHIFT_JIS = "ASCL_PRIME-SHIFT-JIS"
        ASCL_SHIFT_JIS = "ASCL_SHIFT-JIS"
        ASCL_TAU_SHIFT_JIS = "ASCL_TAU-SHIFT-JIS"
        ASCL_TIS620 = "ASCL_TIS620"
        ASCL_TIS620_B = "ASCL_TIS620-B"
        Big5 = "Big5"
        Big5_HKSCS = "Big5-HKSCS"
        BOCU_1 = "BOCU-1"
        CESU_8 = "CESU-8"
        ebcdic_xml_us = "ebcdic-xml-us"
        EUC_KR = "EUC-KR"
        GB_2312_80 = "GB_2312-80"
        gb18030_gb18030 = "gb18030 gb18030"
        GB2312 = "GB2312"
        GBK = "GBK"
        hp_roman8 = "hp-roman8"
        HZ_HZ_GB_2312 = "HZ HZ-GB-2312"
        ibm_1006_P100_1995 = "ibm-1006_P100-1995"
        ibm_1025_P100_1995 = "ibm-1025_P100-1995"
        ibm_1026_P100_1995 = "ibm-1026_P100-1995"
        ibm_1047_P100_1995 = "ibm-1047_P100-1995"
        ibm_1047_P100_1995_swaplfnl = "ibm-1047_P100-1995,swaplfnl"
        ibm_1051_P100_1995 = "ibm-1051_P100-1995"
        ibm_1089_P100_1995 = "ibm-1089_P100-1995"
        ibm_1097_P100_1995 = "ibm-1097_P100-1995"
        ibm_1098_P100_1995 = "ibm-1098_P100-1995"
        ibm_1112_P100_1995 = "ibm-1112_P100-1995"
        ibm_1122_P100_1999 = "ibm-1122_P100-1999"
        ibm_1123_P100_1995 = "ibm-1123_P100-1995"
        ibm_1124_P100_1996 = "ibm-1124_P100-1996"
        ibm_1125_P100_1997 = "ibm-1125_P100-1997"
        ibm_1129_P100_1997 = "ibm-1129_P100-1997"
        ibm_1130_P100_1997 = "ibm-1130_P100-1997"
        ibm_1131_P100_1997 = "ibm-1131_P100-1997"
        ibm_1132_P100_1998 = "ibm-1132_P100-1998"
        ibm_1133_P100_1997 = "ibm-1133_P100-1997"
        ibm_1137_P100_1999 = "ibm-1137_P100-1999"
        ibm_1140_P100_1997 = "ibm-1140_P100-1997"
        ibm_1140_P100_1997_swaplfnl = "ibm-1140_P100-1997,swaplfnl"
        ibm_1141_P100_1997 = "ibm-1141_P100-1997"
        ibm_1141_P100_1997_swaplfnl = "ibm-1141_P100-1997,swaplfnl"
        ibm_1142_P100_1997 = "ibm-1142_P100-1997"
        ibm_1142_P100_1997_swaplfnl = "ibm-1142_P100-1997,swaplfnl"
        ibm_1143_P100_1997 = "ibm-1143_P100-1997"
        ibm_1143_P100_1997_swaplfnl = "ibm-1143_P100-1997,swaplfnl"
        ibm_1144_P100_1997 = "ibm-1144_P100-1997"
        ibm_1144_P100_1997_swaplfnl = "ibm-1144_P100-1997,swaplfnl"
        ibm_1145_P100_1997 = "ibm-1145_P100-1997"
        ibm_1145_P100_1997_swaplfnl = "ibm-1145_P100-1997,swaplfnl"
        ibm_1146_P100_1997 = "ibm-1146_P100-1997"
        ibm_1146_P100_1997_swaplfnl = "ibm-1146_P100-1997,swaplfnl"
        ibm_1147_P100_1997 = "ibm-1147_P100-1997"
        ibm_1147_P100_1997_swaplfnl = "ibm-1147_P100-1997,swaplfnl"
        ibm_1148_P100_1997 = "ibm-1148_P100-1997"
        ibm_1148_P100_1997_swaplfnl = "ibm-1148_P100-1997,swaplfnl"
        ibm_1149_P100_1997 = "ibm-1149_P100-1997"
        ibm_1149_P100_1997_swaplfnl = "ibm-1149_P100-1997,swaplfnl"
        ibm_1153_P100_1999 = "ibm-1153_P100-1999"
        ibm_1153_P100_1999_swaplfnl = "ibm-1153_P100-1999,swaplfnl"
        ibm_1154_P100_1999 = "ibm-1154_P100-1999"
        ibm_1155_P100_1999 = "ibm-1155_P100-1999"
        ibm_1156_P100_1999 = "ibm-1156_P100-1999"
        ibm_1157_P100_1999 = "ibm-1157_P100-1999"
        ibm_1158_P100_1999 = "ibm-1158_P100-1999"
        ibm_1160_P100_1999 = "ibm-1160_P100-1999"
        ibm_1162_P100_1999 = "ibm-1162_P100-1999"
        ibm_1164_P100_1999 = "ibm-1164_P100-1999"
        ibm_1168_P100_2002 = "ibm-1168_P100-2002"
        ibm_1250_P100_1995 = "ibm-1250_P100-1995"
        ibm_1251_P100_1995 = "ibm-1251_P100-1995"
        ibm_1252_P100_2000 = "ibm-1252_P100-2000"
        ibm_1253_P100_1995 = "ibm-1253_P100-1995"
        ibm_1254_P100_1995 = "ibm-1254_P100-1995"
        ibm_1255_P100_1995 = "ibm-1255_P100-1995"
        ibm_1256_P110_1997 = "ibm-1256_P110-1997"
        ibm_1257_P100_1995 = "ibm-1257_P100-1995"
        ibm_1258_P100_1997 = "ibm-1258_P100-1997"
        ibm_12712_P100_1998 = "ibm-12712_P100-1998"
        ibm_12712_P100_1998_swaplfnl = "ibm-12712_P100-1998,swaplfnl"
        ibm_1276_P100_1995 = "ibm-1276_P100-1995"
        ibm_1277_P100_1995 = "ibm-1277_P100-1995"
        ibm_1363_P110_1997 = "ibm-1363_P110-1997"
        ibm_1363_P11B_1998 = "ibm-1363_P11B-1998"
        ibm_1364_P110_1997 = "ibm-1364_P110-1997"
        ibm_1364_P110_2007 = "ibm-1364_P110-2007"
        ibm_1371_P100_1999 = "ibm-1371_P100-1999"
        ibm_1373_P100_2002 = "ibm-1373_P100-2002"
        ibm_1375_P100_2003 = "ibm-1375_P100-2003"
        ibm_1375_P100_2007 = "ibm-1375_P100-2007"
        ibm_1381_P110_1999 = "ibm-1381_P110-1999"
        ibm_1383_P110_1999 = "ibm-1383_P110-1999"
        ibm_1386_P100_2001 = "ibm-1386_P100-2001"
        ibm_1386_P100_2002 = "ibm-1386_P100-2002"
        ibm_1388_P103_2001 = "ibm-1388_P103-2001"
        ibm_1390_P110_2003 = "ibm-1390_P110-2003"
        ibm_1399_P110_2003 = "ibm-1399_P110-2003"
        ibm_16684_P110_2003 = "ibm-16684_P110-2003"
        ibm_16804_X110_1999 = "ibm-16804_X110-1999"
        ibm_16804_X110_1999_swaplfnl = "ibm-16804_X110-1999,swaplfnl"
        ibm_273_P100_1995 = "ibm-273_P100-1995"
        ibm_277_P100_1995 = "ibm-277_P100-1995"
        ibm_278_P100_1995 = "ibm-278_P100-1995"
        ibm_280_P100_1995 = "ibm-280_P100-1995"
        ibm_284_P100_1995 = "ibm-284_P100-1995"
        ibm_285_P100_1995 = "ibm-285_P100-1995"
        ibm_290_P100_1995 = "ibm-290_P100-1995"
        ibm_297_P100_1995 = "ibm-297_P100-1995"
        ibm_33722_P120_1999 = "ibm-33722_P120-1999"
        ibm_33722_P12A_P12A_2009_U2_Extended_UNIX_Code_Packed_Format_for_Japanese = (
            "ibm-33722_P12A_P12A-2009_U2 Extended_UNIX_Code_Packed_Format_for_Japanese"
        )
        ibm_33722_P12A_1999 = "ibm-33722_P12A-1999"
        ibm_367_P100_1995 = "ibm-367_P100-1995"
        ibm_37_P100_1995 = "ibm-37_P100-1995"
        ibm_37_P100_1995_swaplfnl = "ibm-37_P100-1995,swaplfnl"
        ibm_420_X120_1999 = "ibm-420_X120-1999"
        ibm_424_P100_1995 = "ibm-424_P100-1995"
        ibm_437_P100_1995 = "ibm-437_P100-1995"
        ibm_4517_P100_2005 = "ibm-4517_P100-2005"
        ibm_4899_P100_1998 = "ibm-4899_P100-1998"
        ibm_4909_P100_1999 = "ibm-4909_P100-1999"
        ibm_4971_P100_1999 = "ibm-4971_P100-1999"
        ibm_500_P100_1995 = "ibm-500_P100-1995"
        ibm_5012_P100_1999 = "ibm-5012_P100-1999"
        ibm_5123_P100_1999 = "ibm-5123_P100-1999"
        ibm_5346_P100_1998 = "ibm-5346_P100-1998"
        ibm_5347_P100_1998 = "ibm-5347_P100-1998"
        ibm_5348_P100_1997 = "ibm-5348_P100-1997"
        ibm_5349_P100_1998 = "ibm-5349_P100-1998"
        ibm_5350_P100_1998 = "ibm-5350_P100-1998"
        ibm_5351_P100_1998 = "ibm-5351_P100-1998"
        ibm_5352_P100_1998 = "ibm-5352_P100-1998"
        ibm_5353_P100_1998 = "ibm-5353_P100-1998"
        ibm_5354_P100_1998 = "ibm-5354_P100-1998"
        ibm_5471_P100_2006 = "ibm-5471_P100-2006"
        ibm_5478_P100_1995 = "ibm-5478_P100-1995"
        ibm_720_P100_1997 = "ibm-720_P100-1997"
        ibm_737_P100_1997 = "ibm-737_P100-1997"
        ibm_775_P100_1996 = "ibm-775_P100-1996"
        ibm_803_P100_1999 = "ibm-803_P100-1999"
        ibm_813_P100_1995 = "ibm-813_P100-1995"
        ibm_838_P100_1995 = "ibm-838_P100-1995"
        ibm_8482_P100_1999 = "ibm-8482_P100-1999"
        ibm_850_P100_1995 = "ibm-850_P100-1995"
        ibm_851_P100_1995 = "ibm-851_P100-1995"
        ibm_852_P100_1995 = "ibm-852_P100-1995"
        ibm_855_P100_1995 = "ibm-855_P100-1995"
        ibm_856_P100_1995 = "ibm-856_P100-1995"
        ibm_857_P100_1995 = "ibm-857_P100-1995"
        ibm_858_P100_1997 = "ibm-858_P100-1997"
        ibm_860_P100_1995 = "ibm-860_P100-1995"
        ibm_861_P100_1995 = "ibm-861_P100-1995"
        ibm_862_P100_1995 = "ibm-862_P100-1995"
        ibm_863_P100_1995 = "ibm-863_P100-1995"
        ibm_864_X110_1999 = "ibm-864_X110-1999"
        ibm_865_P100_1995 = "ibm-865_P100-1995"
        ibm_866_P100_1995 = "ibm-866_P100-1995"
        ibm_867_P100_1998 = "ibm-867_P100-1998"
        ibm_868_P100_1995 = "ibm-868_P100-1995"
        ibm_869_P100_1995 = "ibm-869_P100-1995"
        ibm_870_P100_1995 = "ibm-870_P100-1995"
        ibm_871_P100_1995 = "ibm-871_P100-1995"
        ibm_874_P100_1995 = "ibm-874_P100-1995"
        ibm_875_P100_1995 = "ibm-875_P100-1995"
        ibm_878_P100_1996 = "ibm-878_P100-1996"
        ibm_897_P100_1995 = "ibm-897_P100-1995"
        ibm_9005_X110_2007 = "ibm-9005_X110-2007"
        ibm_901_P100_1999 = "ibm-901_P100-1999"
        ibm_902_P100_1999 = "ibm-902_P100-1999"
        ibm_9067_X100_2005 = "ibm-9067_X100-2005"
        ibm_912_P100_1995 = "ibm-912_P100-1995"
        ibm_913_P100_2000 = "ibm-913_P100-2000"
        ibm_914_P100_1995 = "ibm-914_P100-1995"
        ibm_915_P100_1995 = "ibm-915_P100-1995"
        ibm_916_P100_1995 = "ibm-916_P100-1995"
        ibm_918_P100_1995 = "ibm-918_P100-1995"
        ibm_920_P100_1995 = "ibm-920_P100-1995"
        ibm_921_P100_1995 = "ibm-921_P100-1995"
        ibm_922_P100_1999 = "ibm-922_P100-1999"
        ibm_923_P100_1998 = "ibm-923_P100-1998"
        ibm_930_P120_1999 = "ibm-930_P120-1999"
        ibm_933_P110_1995 = "ibm-933_P110-1995"
        ibm_935_P110_1999 = "ibm-935_P110-1999"
        ibm_937_P110_1999 = "ibm-937_P110-1999"
        ibm_939_P120_1999 = "ibm-939_P120-1999"
        ibm_942_P12A_1999 = "ibm-942_P12A-1999"
        ibm_943_P130_1999 = "ibm-943_P130-1999"
        ibm_943_P15A_2003 = "ibm-943_P15A-2003"
        ibm_9447_P100_2002 = "ibm-9447_P100-2002"
        ibm_9448_X100_2005 = "ibm-9448_X100-2005"
        ibm_9449_P100_2002 = "ibm-9449_P100-2002"
        ibm_949_P110_1999 = "ibm-949_P110-1999"
        ibm_949_P11A_1999 = "ibm-949_P11A-1999"
        ibm_950_P110_1999 = "ibm-950_P110-1999"
        ibm_954_P101_2000 = "ibm-954_P101-2000"
        ibm_954_P101_2007 = "ibm-954_P101-2007"
        ibm_964_P110_1999 = "ibm-964_P110-1999"
        ibm_970_P110_P110_2006_U2 = "ibm-970_P110_P110-2006_U2"
        ibm_970_P110_1995 = "ibm-970_P110-1995"
        ibm_971_P100_1995 = "ibm-971_P100-1995"
        IBM_Thai = "IBM-Thai"
        IBM00858 = "IBM00858"
        IBM01140 = "IBM01140"
        IBM01141 = "IBM01141"
        IBM01142 = "IBM01142"
        IBM01143 = "IBM01143"
        IBM01144 = "IBM01144"
        IBM01145 = "IBM01145"
        IBM01146 = "IBM01146"
        IBM01147 = "IBM01147"
        IBM01148 = "IBM01148"
        IBM01149 = "IBM01149"
        IBM037 = "IBM037"
        IBM1026 = "IBM1026"
        IBM1047 = "IBM1047"
        IBM273 = "IBM273"
        IBM277 = "IBM277"
        IBM278 = "IBM278"
        IBM280 = "IBM280"
        IBM284 = "IBM284"
        IBM285 = "IBM285"
        IBM290 = "IBM290"
        IBM297 = "IBM297"
        IBM420 = "IBM420"
        IBM424 = "IBM424"
        IBM437 = "IBM437"
        IBM500 = "IBM500"
        IBM775 = "IBM775"
        IBM850 = "IBM850"
        IBM851 = "IBM851"
        IBM852 = "IBM852"
        IBM855 = "IBM855"
        IBM857 = "IBM857"
        IBM860 = "IBM860"
        IBM861 = "IBM861"
        IBM862 = "IBM862"
        IBM863 = "IBM863"
        IBM864 = "IBM864"
        IBM865 = "IBM865"
        IBM866 = "IBM866"
        IBM868 = "IBM868"
        IBM869 = "IBM869"
        IBM870 = "IBM870"
        IBM871 = "IBM871"
        IBM918 = "IBM918"
        IMAP_mailbox_name = "IMAP-mailbox-name"
        ISCII_version_0 = "ISCII,version=0"
        ISCII_version_1 = "ISCII,version=1"
        ISCII_version_2 = "ISCII,version=2"
        ISCII_version_3 = "ISCII,version=3"
        ISCII_version_4 = "ISCII,version=4"
        ISCII_version_5 = "ISCII,version=5"
        ISCII_version_6 = "ISCII,version=6"
        ISCII_version_7 = "ISCII,version=7"
        ISCII_version_8 = "ISCII,version=8"
        ISO_2022_locale_ja_version_0 = "ISO_2022,locale=ja,version=0"
        ISO_2022_locale_ja_version_1 = "ISO_2022,locale=ja,version=1"
        ISO_2022_locale_ja_version_2 = "ISO_2022,locale=ja,version=2"
        ISO_2022_locale_ja_version_3 = "ISO_2022,locale=ja,version=3"
        ISO_2022_locale_ja_version_4 = "ISO_2022,locale=ja,version=4"
        ISO_2022_locale_ko_version_0 = "ISO_2022,locale=ko,version=0"
        ISO_2022_locale_ko_version_1 = "ISO_2022,locale=ko,version=1"
        ISO_2022_locale_zh_version_0 = "ISO_2022,locale=zh,version=0"
        ISO_2022_locale_zh_version_1 = "ISO_2022,locale=zh,version=1"
        ISO_2022_locale_zh_version_2 = "ISO_2022,locale=zh,version=2"
        ISO_8859_1_1987 = "ISO_8859-1:1987"
        ISO_8859_2_1987 = "ISO_8859-2:1987"
        ISO_8859_3_1988 = "ISO_8859-3:1988"
        ISO_8859_4_1988 = "ISO_8859-4:1988"
        ISO_8859_5_1988 = "ISO_8859-5:1988"
        ISO_8859_6_1987 = "ISO_8859-6:1987"
        ISO_8859_7_1987 = "ISO_8859-7:1987"
        ISO_8859_8_1988 = "ISO_8859-8:1988"
        ISO_8859_9_1989 = "ISO_8859-9:1989"
        ISO_2022_CN = "ISO-2022-CN"
        ISO_2022_CN_EXT = "ISO-2022-CN-EXT"
        ISO_2022_JP = "ISO-2022-JP"
        ISO_2022_JP_2 = "ISO-2022-JP-2"
        ISO_2022_KR = "ISO-2022-KR"
        iso_8859_10_1998 = "iso-8859_10-1998"
        iso_8859_11_2001 = "iso-8859_11-2001"
        iso_8859_14_1998 = "iso-8859_14-1998"
        ISO_8859_1 = "ISO-8859-1"
        ISO_8859_10 = "ISO-8859-10"
        ISO_8859_13 = "ISO-8859-13"
        ISO_8859_14 = "ISO-8859-14"
        ISO_8859_15 = "ISO-8859-15"
        JIS_Encoding = "JIS_Encoding"
        KOI8_R = "KOI8-R"
        KOI8_U = "KOI8-U"
        KS_C_5601_1987 = "KS_C_5601-1987"
        LMBCS_1 = "LMBCS-1"
        macintosh = "macintosh"
        macos_0_2_10_2 = "macos-0_2-10.2"
        macos_2566_10_2 = "macos-2566-10.2"
        macos_29_10_2 = "macos-29-10.2"
        macos_35_10_2 = "macos-35-10.2"
        macos_6_2_10_4 = "macos-6_2-10.4"
        macos_6_10_2 = "macos-6-10.2"
        macos_7_3_10_2 = "macos-7_3-10.2"
        SCSU = "SCSU"
        Shift_JIS = "Shift_JIS"
        TIS_620 = "TIS-620"
        US_ASCII = "US-ASCII"
        UTF_16 = "UTF-16"
        UTF_16_version_1 = "UTF-16,version=1"
        UTF_16_version_2 = "UTF-16,version=2"
        UTF_16BE = "UTF-16BE"
        UTF_16BE_version_1 = "UTF-16BE,version=1"
        UTF_16LE = "UTF-16LE"
        UTF_16LE_version_1 = "UTF-16LE,version=1"
        UTF_32 = "UTF-32"
        UTF_32BE = "UTF-32BE"
        UTF_32LE = "UTF-32LE"
        UTF_7 = "UTF-7"
        UTF_8 = "UTF-8"
        UTF16_OppositeEndian = "UTF16_OppositeEndian"
        UTF16_PlatformEndian = "UTF16_PlatformEndian"
        UTF32_OppositeEndian = "UTF32_OppositeEndian"
        UTF32_PlatformEndian = "UTF32_PlatformEndian"
        windows_1250 = "windows-1250"
        windows_1251 = "windows-1251"
        windows_1252 = "windows-1252"
        windows_1253 = "windows-1253"
        windows_1254 = "windows-1254"
        windows_1255 = "windows-1255"
        windows_1256 = "windows-1256"
        windows_1256_2000 = "windows-1256-2000"
        windows_1257 = "windows-1257"
        windows_1258 = "windows-1258"
        windows_874_2000 = "windows-874-2000"
        windows_936_2000 = "windows-936-2000"
        windows_949_2000 = "windows-949-2000"
        windows_950_2000 = "windows-950-2000"
        x11_compound_text = "x11-compound-text"

    class AllowPerColumnMapping(Enum):
        """Enum for the AllowPerColumnMapping property."""

        false = "False"
        true = "True"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class FinalDelimiter(Enum):
        """Enum for the FinalDelimiter property."""

        custom = " "
        ws = "ws"
        end = "end"
        none = "none"
        null = "null"
        comma = "','"
        tab = "'\t'"

    class FillChar(Enum):
        """Enum for the FillChar property."""

        custom_fill_char = -1
        null = 0

    class CheckIntact(Enum):
        """Enum for the CheckIntact property."""

        check_intact = "check_intact"

    class RecordDelimiter(Enum):
        """Enum for the RecordDelimiter property."""

        custom = " "
        newline = "'\n'"
        null = "null"

    class RecordPrefix(Enum):
        """Enum for the RecordPrefix property."""

        one = 1
        two = 2
        four = 4

    class RecordLength(Enum):
        """Enum for the RecordLength property."""

        custom = " "
        fixed = "fixed"

    class RecordType(Enum):
        """Enum for the RecordType property."""

        type_implicit = "{type=implicit}"
        type_varying = "{type=varying}"
        type_varying_format_V = "{type=varying, format=V}"
        type_varying_format_VB = "{type=varying, format=VB}"
        type_varying_format_VBS = "{type=varying, format=VBS}"
        type_varying_format_VR = "{type=varying, format=VR}"
        type_varying_format_VS = "{type=varying, format=VS}"

    class Delimiter(Enum):
        """Enum for the Delimiter property."""

        custom = " "
        ws = "ws"
        end = "end"
        none = "none"
        null = "null"
        comma = "','"
        tab = "'\t'"

    class Quote(Enum):
        """Enum for the Quote property."""

        custom = " "
        single = "single"
        double = "double"
        none = "none"

    class NullFieldValueSeparator(Enum):
        """Enum for the NullFieldValueSeparator property."""

        space = " "
        comma = "','"

    class PrintField(Enum):
        """Enum for the PrintField property."""

        print_field = "print_field"

    class VectorPrefix(Enum):
        """Enum for the VectorPrefix property."""

        one = 1
        two = 2
        four = 4

    class PrefixBytes(Enum):
        """Enum for the PrefixBytes property."""

        one = 1
        two = 2
        four = 4

    class ByteOrder(Enum):
        """Enum for the ByteOrder property."""

        little_endian = "little_endian"
        big_endian = "big_endian"
        native_endian = "native_endian"

    class CharacterSet(Enum):
        """Enum for the CharacterSet property."""

        ebcdic = "ebcdic"
        ascii = "ascii"

    class DataFormat(Enum):
        """Enum for the DataFormat property."""

        binary = "binary"
        text = "text"

    class PadChar(Enum):
        """Enum for the PadChar property."""

        custom = " "
        false_ = "' '"
        null = "null"

    class ExportEbcdicAsAscii(Enum):
        """Enum for the ExportEbcdicAsAscii property."""

        export_ebcdic_as_ascii = "export_ebcdic_as_ascii"

    class ImportAsciiAsEbcdic(Enum):
        """Enum for the ImportAsciiAsEbcdic property."""

        import_ascii_as_ebcdic = "import_ascii_as_ebcdic"

    class AllowAllZeros(Enum):
        """Enum for the AllowAllZeros property."""

        nofix_zero = "nofix_zero"
        fix_zero = "fix_zero"

    class DecimalSeparator(Enum):
        """Enum for the DecimalSeparator property."""

        custom = " "
        comma = "','"
        period = "'.'"

    class DecimalPacked(Enum):
        """Enum for the DecimalPacked property."""

        packed = "packed"
        separate = "separate"
        zoned = "zoned"
        overpunch = "overpunch"

    class DecimalPackedCheck(Enum):
        """Enum for the DecimalPackedCheck property."""

        check = "check"
        nocheck = "nocheck"

    class DecimalPackedSigned(Enum):
        """Enum for the DecimalPackedSigned property."""

        signed = "signed"
        unsigned = "unsigned"

    class AllowSignedImport(Enum):
        """Enum for the AllowSignedImport property."""

        allow_signed_import = "allow_signed_import"

    class DecimalPackedSignPosition(Enum):
        """Enum for the DecimalPackedSignPosition property."""

        trailing = "trailing"
        leading = "leading"

    class Rounding(Enum):
        """Enum for the Rounding property."""

        ceil = "ceil"
        floor = "floor"
        round_inf = "round_inf"
        trunc_zero = "trunc_zero"

    class IsJulian(Enum):
        """Enum for the IsJulian property."""

        julian = "julian"

    class IsMidnightSeconds(Enum):
        """Enum for the IsMidnightSeconds property."""

        midnight_seconds = "midnight_seconds"

    class RecLevelOption(Enum):
        """Enum for the RecLevelOption property."""

        final_delimiter = "final_delimiter"
        fill = "fill"
        final_delim_string = "final_delim_string"
        intact = "intact"
        record_delimiter = "record_delimiter"
        record_delim_string = "record_delim_string"
        record_length = "record_length"
        record_prefix = "record_prefix"
        record_format = "record_format"

    class FieldOption(Enum):
        """Enum for the FieldOption property."""

        delimiter = "delimiter"
        quote = "quote"
        actual_length = "actual_length"
        delim_string = "delim_string"
        null_length = "null_length"
        null_field = "null_field"
        prefix_bytes = "prefix_bytes"
        print_field = "print_field"
        vector_prefix = "vector_prefix"

    class GeneralOption(Enum):
        """Enum for the GeneralOption property."""

        byte_order = "byte_order"
        charset = "charset"
        data_format = "data_format"
        max_width = "max_width"
        field_width = "field_width"
        padchar = "padchar"

    class StringOption(Enum):
        """Enum for the StringOption property."""

        export_ebcdic_as_ascii = "export_ebcdic_as_ascii"
        import_ascii_as_ebcdic = "import_ascii_as_ebcdic"

    class DecimalOption(Enum):
        """Enum for the DecimalOption property."""

        allow_all_zeros = "allow_all_zeros"
        decimal_separator = "decimal_separator"
        decimal_packed = "decimal_packed"
        precision = "precision"
        round = "round"
        scale = "scale"

    class NumericOption(Enum):
        """Enum for the NumericOption property."""

        c_format = "c_format"
        in_format = "in_format"
        out_format = "out_format"

    class DateOption(Enum):
        """Enum for the DateOption property."""

        none = "none"
        days_since = "days_since"
        date_format = "date_format"
        is_julian = "is_julian"

    class TimeOption(Enum):
        """Enum for the TimeOption property."""

        none = "none"
        time_format = "time_format"
        is_midnight_seconds = "is_midnight_seconds"

    class TimestampOption(Enum):
        """Enum for the TimestampOption property."""

        none = "none"
        timestamp_format = "timestamp_format"


class MODIFY:
    """Enums for properties in the MODIFY stage."""

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class ENCODE:
    """Enums for properties in the ENCODE stage."""

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_set = -2
        clear = 0
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class LOOKUP:
    """Enums for properties in the LOOKUP stage."""

    class AllowDups(Enum):
        """Enum for the AllowDups property."""

        true = "allow_dups"
        false = " "

    class ConditionNotMet(Enum):
        """Enum for the ConditionNotMet property."""

        fail = "fail"
        cont = "continue"
        drop = "drop"
        reject = "reject"

    class LookupFail(Enum):
        """Enum for the LookupFail property."""

        fail = "fail"
        cont = "continue"
        drop = "drop"
        reject = "reject"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class CollationSequence(Enum):
        """Enum for the CollationSequence property."""

        OFF = "OFF"
        af = "af"
        af_NA = "af_NA"
        af_ZA = "af_ZA"
        agq = "agq"
        agq_CM = "agq_CM"
        ak = "ak"
        ak_GH = "ak_GH"
        am = "am"
        am_ET = "am_ET"
        ar = "ar"
        ar_001 = "ar_001"
        ar_AE = "ar_AE"
        ar_BH = "ar_BH"
        ar_DJ = "ar_DJ"
        ar_DZ = "ar_DZ"
        ar_EG = "ar_EG"
        ar_EH = "ar_EH"
        ar_ER = "ar_ER"
        ar_IL = "ar_IL"
        ar_IQ = "ar_IQ"
        ar_JO = "ar_JO"
        ar_KM = "ar_KM"
        ar_KW = "ar_KW"
        ar_LB = "ar_LB"
        ar_LY = "ar_LY"
        ar_MA = "ar_MA"
        ar_MR = "ar_MR"
        ar_OM = "ar_OM"
        ar_PS = "ar_PS"
        ar_QA = "ar_QA"
        ar_SA = "ar_SA"
        ar_SD = "ar_SD"
        ar_SO = "ar_SO"
        ar_SY = "ar_SY"
        ar_TD = "ar_TD"
        ar_TN = "ar_TN"
        ar_YE = "ar_YE"
        as_ = "as"
        as_IN = "as_IN"
        asa = "asa"
        asa_TZ = "asa_TZ"
        az = "az"
        az_Cyrl = "az_Cyrl"
        az_Cyrl_AZ = "az_Cyrl_AZ"
        az_Latn = "az_Latn"
        az_Latn_AZ = "az_Latn_AZ"
        bas = "bas"
        bas_CM = "bas_CM"
        be = "be"
        be_BY = "be_BY"
        bem = "bem"
        bem_ZM = "bem_ZM"
        bez = "bez"
        bez_TZ = "bez_TZ"
        bg = "bg"
        bg_BG = "bg_BG"
        bm = "bm"
        bm_ML = "bm_ML"
        bn = "bn"
        bn_BD = "bn_BD"
        bn_IN = "bn_IN"
        bo = "bo"
        bo_CN = "bo_CN"
        bo_IN = "bo_IN"
        br = "br"
        br_FR = "br_FR"
        brx = "brx"
        brx_IN = "brx_IN"
        bs = "bs"
        bs_Cyrl = "bs_Cyrl"
        bs_Cyrl_BA = "bs_Cyrl_BA"
        bs_Latn = "bs_Latn"
        bs_Latn_BA = "bs_Latn_BA"
        ca = "ca"
        ca_AD = "ca_AD"
        ca_ES = "ca_ES"
        cgg = "cgg"
        cgg_UG = "cgg_UG"
        chr = "chr"
        chr_US = "chr_US"
        cs = "cs"
        cs_CZ = "cs_CZ"
        cy = "cy"
        cy_GB = "cy_GB"
        da = "da"
        da_DK = "da_DK"
        dav = "dav"
        dav_KE = "dav_KE"
        de = "de"
        de_AT = "de_AT"
        de_BE = "de_BE"
        de_CH = "de_CH"
        de_DE = "de_DE"
        de_LI = "de_LI"
        de_LU = "de_LU"
        dje = "dje"
        dje_NE = "dje_NE"
        dua = "dua"
        dua_CM = "dua_CM"
        dyo = "dyo"
        dyo_SN = "dyo_SN"
        dz = "dz"
        dz_BT = "dz_BT"
        ebu = "ebu"
        ebu_KE = "ebu_KE"
        ee = "ee"
        ee_GH = "ee_GH"
        ee_TG = "ee_TG"
        el = "el"
        el_CY = "el_CY"
        el_GR = "el_GR"
        en = "en"
        en_150 = "en_150"
        en_AG = "en_AG"
        en_AS = "en_AS"
        en_AU = "en_AU"
        en_BB = "en_BB"
        en_BE = "en_BE"
        en_BM = "en_BM"
        en_BS = "en_BS"
        en_BW = "en_BW"
        en_BZ = "en_BZ"
        en_CA = "en_CA"
        en_CM = "en_CM"
        en_DM = "en_DM"
        en_FJ = "en_FJ"
        en_FM = "en_FM"
        en_GB = "en_GB"
        en_GD = "en_GD"
        en_GG = "en_GG"
        en_GH = "en_GH"
        en_GI = "en_GI"
        en_GM = "en_GM"
        en_GU = "en_GU"
        en_GY = "en_GY"
        en_HK = "en_HK"
        en_IE = "en_IE"
        en_IM = "en_IM"
        en_IN = "en_IN"
        en_JE = "en_JE"
        en_JM = "en_JM"
        en_KE = "en_KE"
        en_KI = "en_KI"
        en_KN = "en_KN"
        en_KY = "en_KY"
        en_LC = "en_LC"
        en_LR = "en_LR"
        en_LS = "en_LS"
        en_MG = "en_MG"
        en_MH = "en_MH"
        en_MP = "en_MP"
        en_MT = "en_MT"
        en_MU = "en_MU"
        en_MW = "en_MW"
        en_NA = "en_NA"
        en_NG = "en_NG"
        en_NZ = "en_NZ"
        en_PG = "en_PG"
        en_PH = "en_PH"
        en_PK = "en_PK"
        en_PR = "en_PR"
        en_PW = "en_PW"
        en_SB = "en_SB"
        en_SC = "en_SC"
        en_SG = "en_SG"
        en_SL = "en_SL"
        en_SS = "en_SS"
        en_SZ = "en_SZ"
        en_TC = "en_TC"
        en_TO = "en_TO"
        en_TT = "en_TT"
        en_TZ = "en_TZ"
        en_UG = "en_UG"
        en_UM = "en_UM"
        en_US = "en_US"
        en_US_POSIX = "en_US_POSIX"
        en_VC = "en_VC"
        en_VG = "en_VG"
        en_VI = "en_VI"
        en_VU = "en_VU"
        en_WS = "en_WS"
        en_ZA = "en_ZA"
        en_ZM = "en_ZM"
        en_ZW = "en_ZW"
        eo = "eo"
        es = "es"
        es_419 = "es_419"
        es_AR = "es_AR"
        es_BO = "es_BO"
        es_CL = "es_CL"
        es_CO = "es_CO"
        es_CR = "es_CR"
        es_CU = "es_CU"
        es_DO = "es_DO"
        es_EA = "es_EA"
        es_EC = "es_EC"
        es_ES = "es_ES"
        es_GQ = "es_GQ"
        es_GT = "es_GT"
        es_HN = "es_HN"
        es_IC = "es_IC"
        es_MX = "es_MX"
        es_NI = "es_NI"
        es_PA = "es_PA"
        es_PE = "es_PE"
        es_PH = "es_PH"
        es_PR = "es_PR"
        es_PY = "es_PY"
        es_SV = "es_SV"
        es_US = "es_US"
        es_UY = "es_UY"
        es_VE = "es_VE"
        et = "et"
        et_EE = "et_EE"
        eu = "eu"
        eu_ES = "eu_ES"
        ewo = "ewo"
        ewo_CM = "ewo_CM"
        fa = "fa"
        fa_AF = "fa_AF"
        fa_IR = "fa_IR"
        ff = "ff"
        ff_SN = "ff_SN"
        fi = "fi"
        fi_FI = "fi_FI"
        fil = "fil"
        fil_PH = "fil_PH"
        fo = "fo"
        fo_FO = "fo_FO"
        fr = "fr"
        fr_BE = "fr_BE"
        fr_BF = "fr_BF"
        fr_BI = "fr_BI"
        fr_BJ = "fr_BJ"
        fr_BL = "fr_BL"
        fr_CA = "fr_CA"
        fr_CD = "fr_CD"
        fr_CF = "fr_CF"
        fr_CG = "fr_CG"
        fr_CH = "fr_CH"
        fr_CI = "fr_CI"
        fr_CM = "fr_CM"
        fr_DJ = "fr_DJ"
        fr_DZ = "fr_DZ"
        fr_FR = "fr_FR"
        fr_GA = "fr_GA"
        fr_GF = "fr_GF"
        fr_GN = "fr_GN"
        fr_GP = "fr_GP"
        fr_GQ = "fr_GQ"
        fr_HT = "fr_HT"
        fr_KM = "fr_KM"
        fr_LU = "fr_LU"
        fr_MA = "fr_MA"
        fr_MC = "fr_MC"
        fr_MF = "fr_MF"
        fr_MG = "fr_MG"
        fr_ML = "fr_ML"
        fr_MQ = "fr_MQ"
        fr_MR = "fr_MR"
        fr_MU = "fr_MU"
        fr_NC = "fr_NC"
        fr_NE = "fr_NE"
        fr_PF = "fr_PF"
        fr_RE = "fr_RE"
        fr_RW = "fr_RW"
        fr_SC = "fr_SC"
        fr_SN = "fr_SN"
        fr_SY = "fr_SY"
        fr_TD = "fr_TD"
        fr_TG = "fr_TG"
        fr_TN = "fr_TN"
        fr_VU = "fr_VU"
        fr_YT = "fr_YT"
        ga = "ga"
        ga_IE = "ga_IE"
        gl = "gl"
        gl_ES = "gl_ES"
        gsw = "gsw"
        gsw_CH = "gsw_CH"
        gu = "gu"
        gu_IN = "gu_IN"
        guz = "guz"
        guz_KE = "guz_KE"
        gv = "gv"
        gv_GB = "gv_GB"
        ha = "ha"
        ha_Latn = "ha_Latn"
        ha_Latn_GH = "ha_Latn_GH"
        ha_Latn_NE = "ha_Latn_NE"
        ha_Latn_NG = "ha_Latn_NG"
        haw = "haw"
        haw_US = "haw_US"
        he = "he"
        he_IL = "he_IL"
        hi = "hi"
        hi_IN = "hi_IN"
        hr = "hr"
        hr_BA = "hr_BA"
        hr_HR = "hr_HR"
        hu = "hu"
        hu_HU = "hu_HU"
        hy = "hy"
        hy_AM = "hy_AM"
        id = "id"
        id_ID = "id_ID"
        ig = "ig"
        ig_NG = "ig_NG"
        ii = "ii"
        ii_CN = "ii_CN"
        is_ = "is"
        is_IS = "is_IS"
        it = "it"
        it_CH = "it_CH"
        it_IT = "it_IT"
        it_SM = "it_SM"
        ja = "ja"
        ja_JP = "ja_JP"
        jgo = "jgo"
        jgo_CM = "jgo_CM"
        jmc = "jmc"
        jmc_TZ = "jmc_TZ"
        ka = "ka"
        ka_GE = "ka_GE"
        kab = "kab"
        kab_DZ = "kab_DZ"
        kam = "kam"
        kam_KE = "kam_KE"
        kde = "kde"
        kde_TZ = "kde_TZ"
        kea = "kea"
        kea_CV = "kea_CV"
        khq = "khq"
        khq_ML = "khq_ML"
        ki = "ki"
        ki_KE = "ki_KE"
        kk = "kk"
        kk_Cyrl = "kk_Cyrl"
        kk_Cyrl_KZ = "kk_Cyrl_KZ"
        kl = "kl"
        kl_GL = "kl_GL"
        kln = "kln"
        kln_KE = "kln_KE"
        km = "km"
        km_KH = "km_KH"
        kn = "kn"
        kn_IN = "kn_IN"
        ko = "ko"
        ko_KP = "ko_KP"
        ko_KR = "ko_KR"
        kok = "kok"
        kok_IN = "kok_IN"
        ks = "ks"
        ks_Arab = "ks_Arab"
        ks_Arab_IN = "ks_Arab_IN"
        ksb = "ksb"
        ksb_TZ = "ksb_TZ"
        ksf = "ksf"
        ksf_CM = "ksf_CM"
        kw = "kw"
        kw_GB = "kw_GB"
        lag = "lag"
        lag_TZ = "lag_TZ"
        lg = "lg"
        lg_UG = "lg_UG"
        ln = "ln"
        ln_AO = "ln_AO"
        ln_CD = "ln_CD"
        ln_CF = "ln_CF"
        ln_CG = "ln_CG"
        lo = "lo"
        lo_LA = "lo_LA"
        lt = "lt"
        lt_LT = "lt_LT"
        lu = "lu"
        lu_CD = "lu_CD"
        luo = "luo"
        luo_KE = "luo_KE"
        luy = "luy"
        luy_KE = "luy_KE"
        lv = "lv"
        lv_LV = "lv_LV"
        mas = "mas"
        mas_KE = "mas_KE"
        mas_TZ = "mas_TZ"
        mer = "mer"
        mer_KE = "mer_KE"
        mfe = "mfe"
        mfe_MU = "mfe_MU"
        mg = "mg"
        mg_MG = "mg_MG"
        mgh = "mgh"
        mgh_MZ = "mgh_MZ"
        mgo = "mgo"
        mgo_CM = "mgo_CM"
        mk = "mk"
        mk_MK = "mk_MK"
        ml = "ml"
        ml_IN = "ml_IN"
        mr = "mr"
        mr_IN = "mr_IN"
        ms = "ms"
        ms_BN = "ms_BN"
        ms_MY = "ms_MY"
        ms_SG = "ms_SG"
        mt = "mt"
        mt_MT = "mt_MT"
        mua = "mua"
        mua_CM = "mua_CM"
        my = "my"
        my_MM = "my_MM"
        naq = "naq"
        naq_NA = "naq_NA"
        nb = "nb"
        nb_NO = "nb_NO"
        nd = "nd"
        nd_ZW = "nd_ZW"
        ne = "ne"
        ne_IN = "ne_IN"
        ne_NP = "ne_NP"
        nl = "nl"
        nl_AW = "nl_AW"
        nl_BE = "nl_BE"
        nl_CW = "nl_CW"
        nl_NL = "nl_NL"
        nl_SR = "nl_SR"
        nl_SX = "nl_SX"
        nmg = "nmg"
        nmg_CM = "nmg_CM"
        nn = "nn"
        nn_NO = "nn_NO"
        nus = "nus"
        nus_SD = "nus_SD"
        nyn = "nyn"
        nyn_UG = "nyn_UG"
        om = "om"
        om_ET = "om_ET"
        om_KE = "om_KE"
        or_ = "or"
        or_IN = "or_IN"
        pa = "pa"
        pa_Arab = "pa_Arab"
        pa_Arab_PK = "pa_Arab_PK"
        pa_Guru = "pa_Guru"
        pa_Guru_IN = "pa_Guru_IN"
        pl = "pl"
        pl_PL = "pl_PL"
        ps = "ps"
        ps_AF = "ps_AF"
        pt = "pt"
        pt_AO = "pt_AO"
        pt_BR = "pt_BR"
        pt_CV = "pt_CV"
        pt_GW = "pt_GW"
        pt_MO = "pt_MO"
        pt_MZ = "pt_MZ"
        pt_PT = "pt_PT"
        pt_ST = "pt_ST"
        pt_TL = "pt_TL"
        rm = "rm"
        rm_CH = "rm_CH"
        rn = "rn"
        rn_BI = "rn_BI"
        ro = "ro"
        ro_MD = "ro_MD"
        ro_RO = "ro_RO"
        rof = "rof"
        rof_TZ = "rof_TZ"
        ru = "ru"
        ru_BY = "ru_BY"
        ru_KG = "ru_KG"
        ru_KZ = "ru_KZ"
        ru_MD = "ru_MD"
        ru_RU = "ru_RU"
        ru_UA = "ru_UA"
        rw = "rw"
        rw_RW = "rw_RW"
        rwk = "rwk"
        rwk_TZ = "rwk_TZ"
        saq = "saq"
        saq_KE = "saq_KE"
        sbp = "sbp"
        sbp_TZ = "sbp_TZ"
        seh = "seh"
        seh_MZ = "seh_MZ"
        ses = "ses"
        ses_ML = "ses_ML"
        sg = "sg"
        sg_CF = "sg_CF"
        shi = "shi"
        shi_Latn = "shi_Latn"
        shi_Latn_MA = "shi_Latn_MA"
        shi_Tfng = "shi_Tfng"
        shi_Tfng_MA = "shi_Tfng_MA"
        si = "si"
        si_LK = "si_LK"
        sk = "sk"
        sk_SK = "sk_SK"
        sl = "sl"
        sl_SI = "sl_SI"
        sn = "sn"
        sn_ZW = "sn_ZW"
        so = "so"
        so_DJ = "so_DJ"
        so_ET = "so_ET"
        so_KE = "so_KE"
        so_SO = "so_SO"
        sq = "sq"
        sq_AL = "sq_AL"
        sq_MK = "sq_MK"
        sr = "sr"
        sr_Cyrl = "sr_Cyrl"
        sr_Cyrl_BA = "sr_Cyrl_BA"
        sr_Cyrl_ME = "sr_Cyrl_ME"
        sr_Cyrl_RS = "sr_Cyrl_RS"
        sr_Latn = "sr_Latn"
        sr_Latn_BA = "sr_Latn_BA"
        sr_Latn_ME = "sr_Latn_ME"
        sr_Latn_RS = "sr_Latn_RS"
        sv = "sv"
        sv_AX = "sv_AX"
        sv_FI = "sv_FI"
        sv_SE = "sv_SE"
        sw = "sw"
        sw_KE = "sw_KE"
        sw_TZ = "sw_TZ"
        sw_UG = "sw_UG"
        swc = "swc"
        swc_CD = "swc_CD"
        ta = "ta"
        ta_IN = "ta_IN"
        ta_LK = "ta_LK"
        ta_MY = "ta_MY"
        ta_SG = "ta_SG"
        te = "te"
        te_IN = "te_IN"
        teo = "teo"
        teo_KE = "teo_KE"
        teo_UG = "teo_UG"
        th = "th"
        th_TH = "th_TH"
        ti = "ti"
        ti_ER = "ti_ER"
        ti_ET = "ti_ET"
        to = "to"
        to_TO = "to_TO"
        tr = "tr"
        tr_CY = "tr_CY"
        tr_TR = "tr_TR"
        twq = "twq"
        twq_NE = "twq_NE"
        tzm = "tzm"
        tzm_Latn = "tzm_Latn"
        tzm_Latn_MA = "tzm_Latn_MA"
        uk = "uk"
        uk_UA = "uk_UA"
        ur = "ur"
        ur_IN = "ur_IN"
        ur_PK = "ur_PK"
        uz = "uz"
        uz_Arab = "uz_Arab"
        uz_Arab_AF = "uz_Arab_AF"
        uz_Cyrl = "uz_Cyrl"
        uz_Cyrl_UZ = "uz_Cyrl_UZ"
        uz_Latn = "uz_Latn"
        uz_Latn_UZ = "uz_Latn_UZ"
        vai = "vai"
        vai_Latn = "vai_Latn"
        vai_Latn_LR = "vai_Latn_LR"
        vai_Vaii = "vai_Vaii"
        vai_Vaii_LR = "vai_Vaii_LR"
        vi = "vi"
        vi_VN = "vi_VN"
        vun = "vun"
        vun_TZ = "vun_TZ"
        xog = "xog"
        xog_UG = "xog_UG"
        yav = "yav"
        yav_CM = "yav_CM"
        yo = "yo"
        yo_NG = "yo_NG"
        zh = "zh"
        zh_Hans = "zh_Hans"
        zh_Hans_CN = "zh_Hans_CN"
        zh_Hans_HK = "zh_Hans_HK"
        zh_Hans_MO = "zh_Hans_MO"
        zh_Hans_SG = "zh_Hans_SG"
        zh_Hant = "zh_Hant"
        zh_Hant_HK = "zh_Hant_HK"
        zh_Hant_MO = "zh_Hant_MO"
        zh_Hant_TW = "zh_Hant_TW"
        zu = "zu"
        zu_ZA = "zu_ZA"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class GlobalconstraintsItems(Enum):
        """Enum for the GlobalconstraintsItems property."""

        custom = " "


class SALESFORCEAPI:
    """Enums for properties in the SALESFORCEAPI stage."""

    class AccessMethod(Enum):
        """Enum for the AccessMethod property."""

        bulk_mode = "bulk_mode"
        real_time_mode = "real_time_mode"

    class LookupType(Enum):
        """Enum for the LookupType property."""

        empty = "empty"
        pxbridge = "pxbridge"

    class ReadOperation(Enum):
        """Enum for the ReadOperation property."""

        get_deleted_delta = "get_deleted_delta"
        get_the_bulk_load_status = "get_the_bulk_load_status"
        get_updated_delta = "get_updated_delta"
        query = "query"
        query_all = "query_all"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class SalesforceConcurrencyMode(Enum):
        """Enum for the SalesforceConcurrencyMode property."""

        parallel = "parallel"
        sequential = "sequential"

    class WriteOperation(Enum):
        """Enum for the WriteOperation property."""

        create = "create"
        delete = "delete"
        update = "update"
        upsert = "upsert"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class MATCH360:
    """Enums for properties in the MATCH360 stage."""

    class DataCategory(Enum):
        """Enum for the DataCategory property."""

        records = "records"
        relationships = "relationships"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class WriteMethod(Enum):
        """Enum for the WriteMethod property."""

        load = "load"
        ongoingsync = "ongoingsync"


class SYBASE:
    """Enums for properties in the SYBASE stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        call = "call"
        call_statement = "call_statement"
        general = "general"
        select = "select"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        call = "call"
        call_statement = "call_statement"
        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class SAPDELTAEXTRACT:
    """Enums for properties in the SAPDELTAEXTRACT stage."""

    class OdpContext(Enum):
        """Enum for the OdpContext property."""

        abap_cds = "abap_cds"
        sapi = "sapi"
        hana = "hana"
        bw = "bw"

    class DataFetchMode(Enum):
        """Enum for the DataFetchMode property."""

        delta_mode = "delta_mode"
        full_mode = "full_mode"
        repetitive_mode = "repetitive_mode"

    class OdpType(Enum):
        """Enum for the OdpType property."""

        master_data_attr = "master_data_attr"
        master_data_hier = "master_data_hier"
        master_data_text = "master_data_text"
        transactional = "transactional"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1


class NETEZZA:
    """Enums for properties in the NETEZZA stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        none = "none"
        random = "random"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class InputMethod(Enum):
        """Enum for the InputMethod property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class CredentialsInputMethodSsl(Enum):
        """Enum for the CredentialsInputMethodSsl property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class POSTGRESQL:
    """Enums for properties in the POSTGRESQL stage."""

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        call = "call"
        call_statement = "call_statement"
        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        block = "block"
        none = "none"
        random = "random"
        row = "row"

    class LookupType(Enum):
        """Enum for the LookupType property."""

        empty = "empty"
        pxbridge = "pxbridge"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        call = "call"
        call_statement = "call_statement"
        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class FTP:
    """Enums for properties in the FTP stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class EscapeCharacter(Enum):
        """Enum for the EscapeCharacter property."""

        question = "<?>"
        backslash = "backslash"
        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class FieldDelimiter(Enum):
        """Enum for the FieldDelimiter property."""

        question = "<?>"
        colon = "colon"
        comma = "comma"
        tab = "tab"

    class FileFormat(Enum):
        """Enum for the FileFormat property."""

        avro = "avro"
        csv = "csv"
        delimited = "delimited"
        excel = "excel"
        json = "json"
        orc = "orc"
        parquet = "parquet"
        sav = "sav"
        xml = "xml"
        sas = "sas"
        shp = "shp"

    class InvalidDataHandling(Enum):
        """Enum for the InvalidDataHandling property."""

        column = "column"
        fail = "fail"
        row = "row"

    class QuoteCharacter(Enum):
        """Enum for the QuoteCharacter property."""

        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        read_single = "read_single"
        read_raw = "read_raw"
        read_raw_multiple_wildcard = "read_raw_multiple_wildcard"
        read_multiple_regex = "read_multiple_regex"
        read_multiple_wildcard = "read_multiple_wildcard"

    class RowDelimiter(Enum):
        """Enum for the RowDelimiter property."""

        question = "<?>"
        new_line = "new_line"
        carriage_return = "carriage_return"
        carriage_return_line_feed = "carriage_return_line_feed"
        line_feed = "line_feed"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_seq = "default_seq"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class MapName(Enum):
        """Enum for the MapName property."""

        Adobe_Standard_Encoding = "Adobe-Standard-Encoding"
        ANSI_X3_4_1968 = "ANSI_X3.4-1968"
        ASCL_ASCII = "ASCL_ASCII"
        ASCL_ASCII_PC1 = "ASCL_ASCII-PC1"
        ASCL_BIG5 = "ASCL_BIG5"
        ASCL_C0_CONTROLS = "ASCL_C0-CONTROLS"
        ASCL_C1_CONTROLS = "ASCL_C1-CONTROLS"
        ASCL_EBCDIC = "ASCL_EBCDIC"
        ASCL_EBCDIC_037 = "ASCL_EBCDIC-037"
        ASCL_EBCDIC_1026 = "ASCL_EBCDIC-1026"
        ASCL_EBCDIC_500V1 = "ASCL_EBCDIC-500V1"
        ASCL_EBCDIC_875 = "ASCL_EBCDIC-875"
        ASCL_EBCDIC_CTRLS = "ASCL_EBCDIC-CTRLS"
        ASCL_EBCDIC_IBM1364 = "ASCL_EBCDIC-IBM1364"
        ASCL_EBCDIC_IBM1371 = "ASCL_EBCDIC-IBM1371"
        ASCL_EBCDIC_IBM933 = "ASCL_EBCDIC-IBM933"
        ASCL_EBCDIC_IBM937 = "ASCL_EBCDIC-IBM937"
        ASCL_EBCDIC_JP_CTRLS = "ASCL_EBCDIC-JP-CTRLS"
        ASCL_EBCDIC_JP_KANA = "ASCL_EBCDIC-JP-KANA"
        ASCL_EBCDIC_JP_KANA_E = "ASCL_EBCDIC-JP-KANA-E"
        ASCL_EBCDIC_JP_KANA_HW = "ASCL_EBCDIC-JP-KANA-HW"
        ASCL_GB2312 = "ASCL_GB2312"
        ASCL_ISO8859_1 = "ASCL_ISO8859-1"
        ASCL_ISO8859_10 = "ASCL_ISO8859-10"
        ASCL_ISO8859_15 = "ASCL_ISO8859-15"
        ASCL_ISO8859_2 = "ASCL_ISO8859-2"
        ASCL_ISO8859_3 = "ASCL_ISO8859-3"
        ASCL_ISO8859_4 = "ASCL_ISO8859-4"
        ASCL_ISO8859_5 = "ASCL_ISO8859-5"
        ASCL_ISO8859_6 = "ASCL_ISO8859-6"
        ASCL_ISO8859_7 = "ASCL_ISO8859-7"
        ASCL_ISO8859_8 = "ASCL_ISO8859-8"
        ASCL_ISO8859_9 = "ASCL_ISO8859-9"
        ASCL_JIS_EUC = "ASCL_JIS-EUC"
        ASCL_JIS_EUC_HWK = "ASCL_JIS-EUC-HWK"
        ASCL_JIS_EUC_P = "ASCL_JIS-EUC-P"
        ASCL_JIS_ROMAN = "ASCL_JIS-ROMAN"
        ASCL_JISX0201 = "ASCL_JISX0201"
        ASCL_JPN_EBCDIC = "ASCL_JPN-EBCDIC"
        ASCL_JPN_EBCDIK = "ASCL_JPN-EBCDIK"
        ASCL_JPN_EBCDIKC_CTRL = "ASCL_JPN-EBCDIKC-CTRL"
        ASCL_JPN_EUC = "ASCL_JPN-EUC"
        ASCL_JPN_EUC_KAT = "ASCL_JPN-EUC-KAT"
        ASCL_JPN_EUC_ONE = "ASCL_JPN-EUC-ONE"
        ASCL_JPN_EUC_RTE = "ASCL_JPN-EUC-RTE"
        ASCL_JPN_EUC_TWO = "ASCL_JPN-EUC-TWO"
        ASCL_JPN_IBM78 = "ASCL_JPN-IBM78"
        ASCL_JPN_IBM83 = "ASCL_JPN-IBM83"
        ASCL_JPN_JEF78 = "ASCL_JPN-JEF78"
        ASCL_JPN_JEF83 = "ASCL_JPN-JEF83"
        ASCL_JPN_JIPSE = "ASCL_JPN-JIPSE"
        ASCL_JPN_JIPSJ = "ASCL_JPN-JIPSJ"
        ASCL_JPN_JIS_RTE = "ASCL_JPN-JIS-RTE"
        ASCL_JPN_JIS8 = "ASCL_JPN-JIS8"
        ASCL_JPN_JIS8EUC_CTRL = "ASCL_JPN-JIS8EUC-CTRL"
        ASCL_JPN_KEIS_RTE = "ASCL_JPN-KEIS-RTE"
        ASCL_JPN_KEIS78 = "ASCL_JPN-KEIS78"
        ASCL_JPN_KEIS83 = "ASCL_JPN-KEIS83"
        ASCL_JPN_NEBCDIK = "ASCL_JPN-NEBCDIK"
        ASCL_JPN_SJIS = "ASCL_JPN-SJIS"
        ASCL_KOI8_R = "ASCL_KOI8-R"
        ASCL_KSC5601 = "ASCL_KSC5601"
        ASCL_KSC5601_1992 = "ASCL_KSC5601-1992"
        ASCL_MAC_GREEK = "ASCL_MAC-GREEK"
        ASCL_MAC_GREEK2 = "ASCL_MAC-GREEK2"
        ASCL_MAC_ROMAN = "ASCL_MAC-ROMAN"
        ASCL_MNEMONICS = "ASCL_MNEMONICS"
        ASCL_MS1250 = "ASCL_MS1250"
        ASCL_MS1251 = "ASCL_MS1251"
        ASCL_MS1252 = "ASCL_MS1252"
        ASCL_MS1253 = "ASCL_MS1253"
        ASCL_MS1254 = "ASCL_MS1254"
        ASCL_MS1255 = "ASCL_MS1255"
        ASCL_MS1256 = "ASCL_MS1256"
        ASCL_MS932 = "ASCL_MS932"
        ASCL_MS932_BASE = "ASCL_MS932-BASE"
        ASCL_MS932_EXTRA = "ASCL_MS932-EXTRA"
        ASCL_MS936 = "ASCL_MS936"
        ASCL_MS936_BASE = "ASCL_MS936-BASE"
        ASCL_MS949 = "ASCL_MS949"
        ASCL_MS950 = "ASCL_MS950"
        ASCL_MS950_BASE = "ASCL_MS950-BASE"
        ASCL_PC1040 = "ASCL_PC1040"
        ASCL_PC1041 = "ASCL_PC1041"
        ASCL_PC437 = "ASCL_PC437"
        ASCL_PC850 = "ASCL_PC850"
        ASCL_PC852 = "ASCL_PC852"
        ASCL_PC855 = "ASCL_PC855"
        ASCL_PC857 = "ASCL_PC857"
        ASCL_PC860 = "ASCL_PC860"
        ASCL_PC861 = "ASCL_PC861"
        ASCL_PC862 = "ASCL_PC862"
        ASCL_PC863 = "ASCL_PC863"
        ASCL_PC864 = "ASCL_PC864"
        ASCL_PC865 = "ASCL_PC865"
        ASCL_PC866 = "ASCL_PC866"
        ASCL_PC869 = "ASCL_PC869"
        ASCL_PC874 = "ASCL_PC874"
        ASCL_PRIME_SHIFT_JIS = "ASCL_PRIME-SHIFT-JIS"
        ASCL_SHIFT_JIS = "ASCL_SHIFT-JIS"
        ASCL_TAU_SHIFT_JIS = "ASCL_TAU-SHIFT-JIS"
        ASCL_TIS620 = "ASCL_TIS620"
        ASCL_TIS620_B = "ASCL_TIS620-B"
        Big5 = "Big5"
        Big5_HKSCS = "Big5-HKSCS"
        BOCU_1 = "BOCU-1"
        CESU_8 = "CESU-8"
        ebcdic_xml_us = "ebcdic-xml-us"
        EUC_KR = "EUC-KR"
        GB_2312_80 = "GB_2312-80"
        gb18030_gb18030 = "gb18030 gb18030"
        GB2312 = "GB2312"
        GBK = "GBK"
        hp_roman8 = "hp-roman8"
        HZ_HZ_GB_2312 = "HZ HZ-GB-2312"
        ibm_1006_P100_1995 = "ibm-1006_P100-1995"
        ibm_1025_P100_1995 = "ibm-1025_P100-1995"
        ibm_1026_P100_1995 = "ibm-1026_P100-1995"
        ibm_1047_P100_1995 = "ibm-1047_P100-1995"
        ibm_1047_P100_1995_swaplfnl = "ibm-1047_P100-1995,swaplfnl"
        ibm_1051_P100_1995 = "ibm-1051_P100-1995"
        ibm_1089_P100_1995 = "ibm-1089_P100-1995"
        ibm_1097_P100_1995 = "ibm-1097_P100-1995"
        ibm_1098_P100_1995 = "ibm-1098_P100-1995"
        ibm_1112_P100_1995 = "ibm-1112_P100-1995"
        ibm_1122_P100_1999 = "ibm-1122_P100-1999"
        ibm_1123_P100_1995 = "ibm-1123_P100-1995"
        ibm_1124_P100_1996 = "ibm-1124_P100-1996"
        ibm_1125_P100_1997 = "ibm-1125_P100-1997"
        ibm_1129_P100_1997 = "ibm-1129_P100-1997"
        ibm_1130_P100_1997 = "ibm-1130_P100-1997"
        ibm_1131_P100_1997 = "ibm-1131_P100-1997"
        ibm_1132_P100_1998 = "ibm-1132_P100-1998"
        ibm_1133_P100_1997 = "ibm-1133_P100-1997"
        ibm_1137_P100_1999 = "ibm-1137_P100-1999"
        ibm_1140_P100_1997 = "ibm-1140_P100-1997"
        ibm_1140_P100_1997_swaplfnl = "ibm-1140_P100-1997,swaplfnl"
        ibm_1141_P100_1997 = "ibm-1141_P100-1997"
        ibm_1141_P100_1997_swaplfnl = "ibm-1141_P100-1997,swaplfnl"
        ibm_1142_P100_1997 = "ibm-1142_P100-1997"
        ibm_1142_P100_1997_swaplfnl = "ibm-1142_P100-1997,swaplfnl"
        ibm_1143_P100_1997 = "ibm-1143_P100-1997"
        ibm_1143_P100_1997_swaplfnl = "ibm-1143_P100-1997,swaplfnl"
        ibm_1144_P100_1997 = "ibm-1144_P100-1997"
        ibm_1144_P100_1997_swaplfnl = "ibm-1144_P100-1997,swaplfnl"
        ibm_1145_P100_1997 = "ibm-1145_P100-1997"
        ibm_1145_P100_1997_swaplfnl = "ibm-1145_P100-1997,swaplfnl"
        ibm_1146_P100_1997 = "ibm-1146_P100-1997"
        ibm_1146_P100_1997_swaplfnl = "ibm-1146_P100-1997,swaplfnl"
        ibm_1147_P100_1997 = "ibm-1147_P100-1997"
        ibm_1147_P100_1997_swaplfnl = "ibm-1147_P100-1997,swaplfnl"
        ibm_1148_P100_1997 = "ibm-1148_P100-1997"
        ibm_1148_P100_1997_swaplfnl = "ibm-1148_P100-1997,swaplfnl"
        ibm_1149_P100_1997 = "ibm-1149_P100-1997"
        ibm_1149_P100_1997_swaplfnl = "ibm-1149_P100-1997,swaplfnl"
        ibm_1153_P100_1999 = "ibm-1153_P100-1999"
        ibm_1153_P100_1999_swaplfnl = "ibm-1153_P100-1999,swaplfnl"
        ibm_1154_P100_1999 = "ibm-1154_P100-1999"
        ibm_1155_P100_1999 = "ibm-1155_P100-1999"
        ibm_1156_P100_1999 = "ibm-1156_P100-1999"
        ibm_1157_P100_1999 = "ibm-1157_P100-1999"
        ibm_1158_P100_1999 = "ibm-1158_P100-1999"
        ibm_1160_P100_1999 = "ibm-1160_P100-1999"
        ibm_1162_P100_1999 = "ibm-1162_P100-1999"
        ibm_1164_P100_1999 = "ibm-1164_P100-1999"
        ibm_1168_P100_2002 = "ibm-1168_P100-2002"
        ibm_1250_P100_1995 = "ibm-1250_P100-1995"
        ibm_1251_P100_1995 = "ibm-1251_P100-1995"
        ibm_1252_P100_2000 = "ibm-1252_P100-2000"
        ibm_1253_P100_1995 = "ibm-1253_P100-1995"
        ibm_1254_P100_1995 = "ibm-1254_P100-1995"
        ibm_1255_P100_1995 = "ibm-1255_P100-1995"
        ibm_1256_P110_1997 = "ibm-1256_P110-1997"
        ibm_1257_P100_1995 = "ibm-1257_P100-1995"
        ibm_1258_P100_1997 = "ibm-1258_P100-1997"
        ibm_12712_P100_1998 = "ibm-12712_P100-1998"
        ibm_12712_P100_1998_swaplfnl = "ibm-12712_P100-1998,swaplfnl"
        ibm_1276_P100_1995 = "ibm-1276_P100-1995"
        ibm_1277_P100_1995 = "ibm-1277_P100-1995"
        ibm_1363_P110_1997 = "ibm-1363_P110-1997"
        ibm_1363_P11B_1998 = "ibm-1363_P11B-1998"
        ibm_1364_P110_1997 = "ibm-1364_P110-1997"
        ibm_1364_P110_2007 = "ibm-1364_P110-2007"
        ibm_1371_P100_1999 = "ibm-1371_P100-1999"
        ibm_1373_P100_2002 = "ibm-1373_P100-2002"
        ibm_1375_P100_2003 = "ibm-1375_P100-2003"
        ibm_1375_P100_2007 = "ibm-1375_P100-2007"
        ibm_1381_P110_1999 = "ibm-1381_P110-1999"
        ibm_1383_P110_1999 = "ibm-1383_P110-1999"
        ibm_1386_P100_2001 = "ibm-1386_P100-2001"
        ibm_1386_P100_2002 = "ibm-1386_P100-2002"
        ibm_1388_P103_2001 = "ibm-1388_P103-2001"
        ibm_1390_P110_2003 = "ibm-1390_P110-2003"
        ibm_1399_P110_2003 = "ibm-1399_P110-2003"
        ibm_16684_P110_2003 = "ibm-16684_P110-2003"
        ibm_16804_X110_1999 = "ibm-16804_X110-1999"
        ibm_16804_X110_1999_swaplfnl = "ibm-16804_X110-1999,swaplfnl"
        ibm_273_P100_1995 = "ibm-273_P100-1995"
        ibm_277_P100_1995 = "ibm-277_P100-1995"
        ibm_278_P100_1995 = "ibm-278_P100-1995"
        ibm_280_P100_1995 = "ibm-280_P100-1995"
        ibm_284_P100_1995 = "ibm-284_P100-1995"
        ibm_285_P100_1995 = "ibm-285_P100-1995"
        ibm_290_P100_1995 = "ibm-290_P100-1995"
        ibm_297_P100_1995 = "ibm-297_P100-1995"
        ibm_33722_P120_1999 = "ibm-33722_P120-1999"
        ibm_33722_P12A_P12A_2009_U2_Extended_UNIX_Code_Packed_Format_for_Japanese = (
            "ibm-33722_P12A_P12A-2009_U2 Extended_UNIX_Code_Packed_Format_for_Japanese"
        )
        ibm_33722_P12A_1999 = "ibm-33722_P12A-1999"
        ibm_367_P100_1995 = "ibm-367_P100-1995"
        ibm_37_P100_1995 = "ibm-37_P100-1995"
        ibm_37_P100_1995_swaplfnl = "ibm-37_P100-1995,swaplfnl"
        ibm_420_X120_1999 = "ibm-420_X120-1999"
        ibm_424_P100_1995 = "ibm-424_P100-1995"
        ibm_437_P100_1995 = "ibm-437_P100-1995"
        ibm_4517_P100_2005 = "ibm-4517_P100-2005"
        ibm_4899_P100_1998 = "ibm-4899_P100-1998"
        ibm_4909_P100_1999 = "ibm-4909_P100-1999"
        ibm_4971_P100_1999 = "ibm-4971_P100-1999"
        ibm_500_P100_1995 = "ibm-500_P100-1995"
        ibm_5012_P100_1999 = "ibm-5012_P100-1999"
        ibm_5123_P100_1999 = "ibm-5123_P100-1999"
        ibm_5346_P100_1998 = "ibm-5346_P100-1998"
        ibm_5347_P100_1998 = "ibm-5347_P100-1998"
        ibm_5348_P100_1997 = "ibm-5348_P100-1997"
        ibm_5349_P100_1998 = "ibm-5349_P100-1998"
        ibm_5350_P100_1998 = "ibm-5350_P100-1998"
        ibm_5351_P100_1998 = "ibm-5351_P100-1998"
        ibm_5352_P100_1998 = "ibm-5352_P100-1998"
        ibm_5353_P100_1998 = "ibm-5353_P100-1998"
        ibm_5354_P100_1998 = "ibm-5354_P100-1998"
        ibm_5471_P100_2006 = "ibm-5471_P100-2006"
        ibm_5478_P100_1995 = "ibm-5478_P100-1995"
        ibm_720_P100_1997 = "ibm-720_P100-1997"
        ibm_737_P100_1997 = "ibm-737_P100-1997"
        ibm_775_P100_1996 = "ibm-775_P100-1996"
        ibm_803_P100_1999 = "ibm-803_P100-1999"
        ibm_813_P100_1995 = "ibm-813_P100-1995"
        ibm_838_P100_1995 = "ibm-838_P100-1995"
        ibm_8482_P100_1999 = "ibm-8482_P100-1999"
        ibm_850_P100_1995 = "ibm-850_P100-1995"
        ibm_851_P100_1995 = "ibm-851_P100-1995"
        ibm_852_P100_1995 = "ibm-852_P100-1995"
        ibm_855_P100_1995 = "ibm-855_P100-1995"
        ibm_856_P100_1995 = "ibm-856_P100-1995"
        ibm_857_P100_1995 = "ibm-857_P100-1995"
        ibm_858_P100_1997 = "ibm-858_P100-1997"
        ibm_860_P100_1995 = "ibm-860_P100-1995"
        ibm_861_P100_1995 = "ibm-861_P100-1995"
        ibm_862_P100_1995 = "ibm-862_P100-1995"
        ibm_863_P100_1995 = "ibm-863_P100-1995"
        ibm_864_X110_1999 = "ibm-864_X110-1999"
        ibm_865_P100_1995 = "ibm-865_P100-1995"
        ibm_866_P100_1995 = "ibm-866_P100-1995"
        ibm_867_P100_1998 = "ibm-867_P100-1998"
        ibm_868_P100_1995 = "ibm-868_P100-1995"
        ibm_869_P100_1995 = "ibm-869_P100-1995"
        ibm_870_P100_1995 = "ibm-870_P100-1995"
        ibm_871_P100_1995 = "ibm-871_P100-1995"
        ibm_874_P100_1995 = "ibm-874_P100-1995"
        ibm_875_P100_1995 = "ibm-875_P100-1995"
        ibm_878_P100_1996 = "ibm-878_P100-1996"
        ibm_897_P100_1995 = "ibm-897_P100-1995"
        ibm_9005_X110_2007 = "ibm-9005_X110-2007"
        ibm_901_P100_1999 = "ibm-901_P100-1999"
        ibm_902_P100_1999 = "ibm-902_P100-1999"
        ibm_9067_X100_2005 = "ibm-9067_X100-2005"
        ibm_912_P100_1995 = "ibm-912_P100-1995"
        ibm_913_P100_2000 = "ibm-913_P100-2000"
        ibm_914_P100_1995 = "ibm-914_P100-1995"
        ibm_915_P100_1995 = "ibm-915_P100-1995"
        ibm_916_P100_1995 = "ibm-916_P100-1995"
        ibm_918_P100_1995 = "ibm-918_P100-1995"
        ibm_920_P100_1995 = "ibm-920_P100-1995"
        ibm_921_P100_1995 = "ibm-921_P100-1995"
        ibm_922_P100_1999 = "ibm-922_P100-1999"
        ibm_923_P100_1998 = "ibm-923_P100-1998"
        ibm_930_P120_1999 = "ibm-930_P120-1999"
        ibm_933_P110_1995 = "ibm-933_P110-1995"
        ibm_935_P110_1999 = "ibm-935_P110-1999"
        ibm_937_P110_1999 = "ibm-937_P110-1999"
        ibm_939_P120_1999 = "ibm-939_P120-1999"
        ibm_942_P12A_1999 = "ibm-942_P12A-1999"
        ibm_943_P130_1999 = "ibm-943_P130-1999"
        ibm_943_P15A_2003 = "ibm-943_P15A-2003"
        ibm_9447_P100_2002 = "ibm-9447_P100-2002"
        ibm_9448_X100_2005 = "ibm-9448_X100-2005"
        ibm_9449_P100_2002 = "ibm-9449_P100-2002"
        ibm_949_P110_1999 = "ibm-949_P110-1999"
        ibm_949_P11A_1999 = "ibm-949_P11A-1999"
        ibm_950_P110_1999 = "ibm-950_P110-1999"
        ibm_954_P101_2000 = "ibm-954_P101-2000"
        ibm_954_P101_2007 = "ibm-954_P101-2007"
        ibm_964_P110_1999 = "ibm-964_P110-1999"
        ibm_970_P110_P110_2006_U2 = "ibm-970_P110_P110-2006_U2"
        ibm_970_P110_1995 = "ibm-970_P110-1995"
        ibm_971_P100_1995 = "ibm-971_P100-1995"
        IBM_Thai = "IBM-Thai"
        IBM00858 = "IBM00858"
        IBM01140 = "IBM01140"
        IBM01141 = "IBM01141"
        IBM01142 = "IBM01142"
        IBM01143 = "IBM01143"
        IBM01144 = "IBM01144"
        IBM01145 = "IBM01145"
        IBM01146 = "IBM01146"
        IBM01147 = "IBM01147"
        IBM01148 = "IBM01148"
        IBM01149 = "IBM01149"
        IBM037 = "IBM037"
        IBM1026 = "IBM1026"
        IBM1047 = "IBM1047"
        IBM273 = "IBM273"
        IBM277 = "IBM277"
        IBM278 = "IBM278"
        IBM280 = "IBM280"
        IBM284 = "IBM284"
        IBM285 = "IBM285"
        IBM290 = "IBM290"
        IBM297 = "IBM297"
        IBM420 = "IBM420"
        IBM424 = "IBM424"
        IBM437 = "IBM437"
        IBM500 = "IBM500"
        IBM775 = "IBM775"
        IBM850 = "IBM850"
        IBM851 = "IBM851"
        IBM852 = "IBM852"
        IBM855 = "IBM855"
        IBM857 = "IBM857"
        IBM860 = "IBM860"
        IBM861 = "IBM861"
        IBM862 = "IBM862"
        IBM863 = "IBM863"
        IBM864 = "IBM864"
        IBM865 = "IBM865"
        IBM866 = "IBM866"
        IBM868 = "IBM868"
        IBM869 = "IBM869"
        IBM870 = "IBM870"
        IBM871 = "IBM871"
        IBM918 = "IBM918"
        IMAP_mailbox_name = "IMAP-mailbox-name"
        ISCII_version_0 = "ISCII,version=0"
        ISCII_version_1 = "ISCII,version=1"
        ISCII_version_2 = "ISCII,version=2"
        ISCII_version_3 = "ISCII,version=3"
        ISCII_version_4 = "ISCII,version=4"
        ISCII_version_5 = "ISCII,version=5"
        ISCII_version_6 = "ISCII,version=6"
        ISCII_version_7 = "ISCII,version=7"
        ISCII_version_8 = "ISCII,version=8"
        ISO_2022_locale_ja_version_0 = "ISO_2022,locale=ja,version=0"
        ISO_2022_locale_ja_version_1 = "ISO_2022,locale=ja,version=1"
        ISO_2022_locale_ja_version_2 = "ISO_2022,locale=ja,version=2"
        ISO_2022_locale_ja_version_3 = "ISO_2022,locale=ja,version=3"
        ISO_2022_locale_ja_version_4 = "ISO_2022,locale=ja,version=4"
        ISO_2022_locale_ko_version_0 = "ISO_2022,locale=ko,version=0"
        ISO_2022_locale_ko_version_1 = "ISO_2022,locale=ko,version=1"
        ISO_2022_locale_zh_version_0 = "ISO_2022,locale=zh,version=0"
        ISO_2022_locale_zh_version_1 = "ISO_2022,locale=zh,version=1"
        ISO_2022_locale_zh_version_2 = "ISO_2022,locale=zh,version=2"
        ISO_8859_1_1987 = "ISO_8859-1:1987"
        ISO_8859_2_1987 = "ISO_8859-2:1987"
        ISO_8859_3_1988 = "ISO_8859-3:1988"
        ISO_8859_4_1988 = "ISO_8859-4:1988"
        ISO_8859_5_1988 = "ISO_8859-5:1988"
        ISO_8859_6_1987 = "ISO_8859-6:1987"
        ISO_8859_7_1987 = "ISO_8859-7:1987"
        ISO_8859_8_1988 = "ISO_8859-8:1988"
        ISO_8859_9_1989 = "ISO_8859-9:1989"
        ISO_2022_CN = "ISO-2022-CN"
        ISO_2022_CN_EXT = "ISO-2022-CN-EXT"
        ISO_2022_JP = "ISO-2022-JP"
        ISO_2022_JP_2 = "ISO-2022-JP-2"
        ISO_2022_KR = "ISO-2022-KR"
        iso_8859_10_1998 = "iso-8859_10-1998"
        iso_8859_11_2001 = "iso-8859_11-2001"
        iso_8859_14_1998 = "iso-8859_14-1998"
        ISO_8859_1 = "ISO-8859-1"
        ISO_8859_10 = "ISO-8859-10"
        ISO_8859_13 = "ISO-8859-13"
        ISO_8859_14 = "ISO-8859-14"
        ISO_8859_15 = "ISO-8859-15"
        JIS_Encoding = "JIS_Encoding"
        KOI8_R = "KOI8-R"
        KOI8_U = "KOI8-U"
        KS_C_5601_1987 = "KS_C_5601-1987"
        LMBCS_1 = "LMBCS-1"
        macintosh = "macintosh"
        macos_0_2_10_2 = "macos-0_2-10.2"
        macos_2566_10_2 = "macos-2566-10.2"
        macos_29_10_2 = "macos-29-10.2"
        macos_35_10_2 = "macos-35-10.2"
        macos_6_2_10_4 = "macos-6_2-10.4"
        macos_6_10_2 = "macos-6-10.2"
        macos_7_3_10_2 = "macos-7_3-10.2"
        SCSU = "SCSU"
        Shift_JIS = "Shift_JIS"
        TIS_620 = "TIS-620"
        US_ASCII = "US-ASCII"
        UTF_16 = "UTF-16"
        UTF_16_version_1 = "UTF-16,version=1"
        UTF_16_version_2 = "UTF-16,version=2"
        UTF_16BE = "UTF-16BE"
        UTF_16BE_version_1 = "UTF-16BE,version=1"
        UTF_16LE = "UTF-16LE"
        UTF_16LE_version_1 = "UTF-16LE,version=1"
        UTF_32 = "UTF-32"
        UTF_32BE = "UTF-32BE"
        UTF_32LE = "UTF-32LE"
        UTF_7 = "UTF-7"
        UTF_8 = "UTF-8"
        UTF16_OppositeEndian = "UTF16_OppositeEndian"
        UTF16_PlatformEndian = "UTF16_PlatformEndian"
        UTF32_OppositeEndian = "UTF32_OppositeEndian"
        UTF32_PlatformEndian = "UTF32_PlatformEndian"
        windows_1250 = "windows-1250"
        windows_1251 = "windows-1251"
        windows_1252 = "windows-1252"
        windows_1253 = "windows-1253"
        windows_1254 = "windows-1254"
        windows_1255 = "windows-1255"
        windows_1256 = "windows-1256"
        windows_1256_2000 = "windows-1256-2000"
        windows_1257 = "windows-1257"
        windows_1258 = "windows-1258"
        windows_874_2000 = "windows-874-2000"
        windows_936_2000 = "windows-936-2000"
        windows_949_2000 = "windows-949-2000"
        windows_950_2000 = "windows-950-2000"
        x11_compound_text = "x11-compound-text"

    class AllowPerColumnMapping(Enum):
        """Enum for the AllowPerColumnMapping property."""

        false = "False"
        true = "True"

    class CodecAvro(Enum):
        """Enum for the CodecAvro property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        null = "null"
        snappy = "snappy"

    class CodecCsv(Enum):
        """Enum for the CodecCsv property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecDelimited(Enum):
        """Enum for the CodecDelimited property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecOrc(Enum):
        """Enum for the CodecOrc property."""

        lz4 = "lz4"
        lzo = "lzo"
        none = "none"
        snappy = "snappy"
        zlib = "zlib"

    class CodecParquet(Enum):
        """Enum for the CodecParquet property."""

        gzip = "gzip"
        uncompressed = "uncompressed"
        snappy = "snappy"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        delete = "delete"
        delete_multiple_prefix = "delete_multiple_prefix"
        write = "write"
        write_raw = "write_raw"


class MONGODB_IBMCLOUD:
    """Enums for properties in the MONGODB_IBMCLOUD stage."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        username_password = "username_password"

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"


class SAPBULKEXTRACT:
    """Enums for properties in the SAPBULKEXTRACT stage."""

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1


class DB2CLOUD:
    """Enums for properties in the DB2CLOUD stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        call = "call"
        call_statement = "call_statement"
        general = "general"
        select = "select"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class InputMethod(Enum):
        """Enum for the InputMethod property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class CredentialsInputMethodSsl(Enum):
        """Enum for the CredentialsInputMethodSsl property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        call = "call"
        call_statement = "call_statement"
        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class PRESTO:
    """Enums for properties in the PRESTO stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        block = "block"
        none = "none"
        row = "row"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1


class AZURE_FILE_STORAGE:
    """Enums for properties in the AZURE_FILE_STORAGE stage."""

    class DSFileFormat(Enum):
        """Enum for the DSFileFormat property."""

        comma_separated_value_csv = "comma-separated_value_csv"
        delimited = "delimited"

    class DSReadMode(Enum):
        """Enum for the DSReadMode property."""

        list_containers_fileshares = "list_containers/fileshares"
        list_files = "list_files"
        read_multiple_files = "read_multiple_files"
        read_single_file = "read_single_file"

    class DelimitedSyntaxQuotes(Enum):
        """Enum for the DelimitedSyntaxQuotes property."""

        double = "double"
        none = "none"
        single = "single"

    class DelimitedSyntaxRecordDef(Enum):
        """Enum for the DelimitedSyntaxRecordDef property."""

        delimited_string = "delimited_string"
        delimited_string_in_a_file = "delimited_string_in_a_file"
        file_header = "file_header"
        none = "none"
        schema_file = "schema_file"

    class LookupType(Enum):
        """Enum for the LookupType property."""

        empty = "empty"
        pxbridge = "pxbridge"

    class RejectMode(Enum):
        """Enum for the RejectMode property."""

        cont = "continue"
        fail = "fail"
        reject = "reject"

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class EscapeCharacter(Enum):
        """Enum for the EscapeCharacter property."""

        question = "<?>"
        backslash = "backslash"
        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class FieldDelimiter(Enum):
        """Enum for the FieldDelimiter property."""

        question = "<?>"
        colon = "colon"
        comma = "comma"
        tab = "tab"

    class FileFormat(Enum):
        """Enum for the FileFormat property."""

        avro = "avro"
        csv = "csv"
        delimited = "delimited"
        excel = "excel"
        json = "json"
        orc = "orc"
        parquet = "parquet"
        sav = "sav"
        xml = "xml"

    class InvalidDataHandling(Enum):
        """Enum for the InvalidDataHandling property."""

        column = "column"
        fail = "fail"
        row = "row"

    class QuoteCharacter(Enum):
        """Enum for the QuoteCharacter property."""

        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        read_single = "read_single"
        read_raw = "read_raw"
        read_raw_multiple_wildcard = "read_raw_multiple_wildcard"
        read_multiple_regex = "read_multiple_regex"
        read_multiple_wildcard = "read_multiple_wildcard"

    class RowDelimiter(Enum):
        """Enum for the RowDelimiter property."""

        question = "<?>"
        new_line = "new_line"
        carriage_return = "carriage_return"
        carriage_return_line_feed = "carriage_return_line_feed"
        line_feed = "line_feed"

    class TableFormat(Enum):
        """Enum for the TableFormat property."""

        deltalake = "deltalake"
        file = "file"
        iceberg = "iceberg"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class DSWriteMode(Enum):
        """Enum for the DSWriteMode property."""

        delete = "delete"
        write = "write"

    class FileExists(Enum):
        """Enum for the FileExists property."""

        do_not_overwrite_file = "do_not_overwrite_file"
        fail = "fail"
        overwrite_file = "overwrite_file"

    class CodecAvro(Enum):
        """Enum for the CodecAvro property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        null = "null"
        snappy = "snappy"

    class CodecCsv(Enum):
        """Enum for the CodecCsv property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecDelimited(Enum):
        """Enum for the CodecDelimited property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecOrc(Enum):
        """Enum for the CodecOrc property."""

        lz4 = "lz4"
        lzo = "lzo"
        none = "none"
        snappy = "snappy"
        zlib = "zlib"

    class CodecParquet(Enum):
        """Enum for the CodecParquet property."""

        gzip = "gzip"
        uncompressed = "uncompressed"
        snappy = "snappy"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class TableDataFileCompressionCodec(Enum):
        """Enum for the TableDataFileCompressionCodec property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        gzip = "gzip"
        lz4 = "lz4"
        lzo = "lzo"
        uncompressed = "uncompressed"
        snappy = "snappy"
        zlib = "zlib"

    class TableDataFileFormat(Enum):
        """Enum for the TableDataFileFormat property."""

        avro = "avro"
        orc = "orc"
        parquet = "parquet"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        delete = "delete"
        write = "write"
        write_raw = "write_raw"


class ORACLE_DATASTAGE:
    """Enums for properties in the ORACLE_DATASTAGE stage."""

    class Disconnect(Enum):
        """Enum for the Disconnect property."""

        never = "0"
        period_inactivity = "1"

    class MarkEndOfWave(Enum):
        """Enum for the MarkEndOfWave property."""

        no = "0"
        yes = "2"

    class IsolationLevel(Enum):
        """Enum for the IsolationLevel property."""

        read_committed = "0"
        read_only = "2"
        serializable = "1"

    class LookupType(Enum):
        """Enum for the LookupType property."""

        empty = ""
        pxbridge = "pxbridge"

    class PartitionedReadsMethod(Enum):
        """Enum for the PartitionedReadsMethod property."""

        min_max_range = "3"
        modulus = "2"
        oracle_partitions = "4"
        rowid_hash = "5"
        rowid_range = "0"
        rowid_round_robin = "1"

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        pl_sql = "1"
        select = "0"

    class TableScope(Enum):
        """Enum for the TableScope property."""

        entire_table = "0"
        single_partition = "1"
        single_subpartition = "2"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class DSRecordOrdering(Enum):
        """Enum for the DSRecordOrdering property."""

        zero = 0
        one = 1
        two = 2

    class ColumnDelimiter(Enum):
        """Enum for the ColumnDelimiter property."""

        comma = "3"
        newline = "1"
        space = "0"
        tab = "2"

    class LoggingClause(Enum):
        """Enum for the LoggingClause property."""

        do_not_include_logging_clause = "0"
        logging = "2"
        no_logging = "1"

    class ParallelClause(Enum):
        """Enum for the ParallelClause property."""

        do_not_include_parallel_clause = "0"
        noparallel = "1"
        parallel = "2"
        preserve_degree_prallelism = "3"

    class IndexMaintenanceOption(Enum):
        """Enum for the IndexMaintenanceOption property."""

        do_not_skip_unusable = "0"
        skip_all = "2"
        skip_unusable = "1"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "0"
        create = "1"
        replace = "2"
        truncate = "3"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        bulk_load = "6"
        delete = "2"
        delete_then_insert = "5"
        insert = "0"
        insert_new_rows_only = "9"
        insert_then_update = "3"
        pl_sql = "8"
        update = "1"
        update_then_insert = "4"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class GENERICS3:
    """Enums for properties in the GENERICS3 stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class EscapeCharacter(Enum):
        """Enum for the EscapeCharacter property."""

        question = "<?>"
        backslash = "backslash"
        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class FieldDelimiter(Enum):
        """Enum for the FieldDelimiter property."""

        question = "<?>"
        colon = "colon"
        comma = "comma"
        tab = "tab"

    class FileFormat(Enum):
        """Enum for the FileFormat property."""

        avro = "avro"
        csv = "csv"
        delimited = "delimited"
        excel = "excel"
        json = "json"
        orc = "orc"
        parquet = "parquet"
        sav = "sav"
        xml = "xml"
        sas = "sas"
        shp = "shp"

    class InvalidDataHandling(Enum):
        """Enum for the InvalidDataHandling property."""

        column = "column"
        fail = "fail"
        row = "row"

    class QuoteCharacter(Enum):
        """Enum for the QuoteCharacter property."""

        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        read_single = "read_single"
        read_raw = "read_raw"
        read_raw_multiple_wildcard = "read_raw_multiple_wildcard"
        read_multiple_regex = "read_multiple_regex"
        read_multiple_wildcard = "read_multiple_wildcard"

    class RowDelimiter(Enum):
        """Enum for the RowDelimiter property."""

        question = "<?>"
        new_line = "new_line"
        carriage_return = "carriage_return"
        carriage_return_line_feed = "carriage_return_line_feed"
        line_feed = "line_feed"

    class TableFormat(Enum):
        """Enum for the TableFormat property."""

        deltalake = "deltalake"
        file = "file"
        iceberg = "iceberg"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class CodecAvro(Enum):
        """Enum for the CodecAvro property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        null = "null"
        snappy = "snappy"

    class CodecCsv(Enum):
        """Enum for the CodecCsv property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecDelimited(Enum):
        """Enum for the CodecDelimited property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecOrc(Enum):
        """Enum for the CodecOrc property."""

        lz4 = "lz4"
        lzo = "lzo"
        none = "none"
        snappy = "snappy"
        zlib = "zlib"

    class CodecParquet(Enum):
        """Enum for the CodecParquet property."""

        gzip = "gzip"
        uncompressed = "uncompressed"
        snappy = "snappy"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class TableDataFileCompressionCodec(Enum):
        """Enum for the TableDataFileCompressionCodec property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        gzip = "gzip"
        lz4 = "lz4"
        lzo = "lzo"
        uncompressed = "uncompressed"
        snappy = "snappy"
        zlib = "zlib"

    class TableDataFileFormat(Enum):
        """Enum for the TableDataFileFormat property."""

        avro = "avro"
        orc = "orc"
        parquet = "parquet"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        delete = "delete"
        write = "write"
        write_raw = "write_raw"


class BOX:
    """Enums for properties in the BOX stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class EscapeCharacter(Enum):
        """Enum for the EscapeCharacter property."""

        question = "<?>"
        backslash = "backslash"
        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class FieldDelimiter(Enum):
        """Enum for the FieldDelimiter property."""

        question = "<?>"
        colon = "colon"
        comma = "comma"
        tab = "tab"

    class FileFormat(Enum):
        """Enum for the FileFormat property."""

        avro = "avro"
        csv = "csv"
        delimited = "delimited"
        excel = "excel"
        json = "json"
        orc = "orc"
        parquet = "parquet"
        sav = "sav"
        xml = "xml"
        sas = "sas"
        shp = "shp"

    class InvalidDataHandling(Enum):
        """Enum for the InvalidDataHandling property."""

        column = "column"
        fail = "fail"
        row = "row"

    class QuoteCharacter(Enum):
        """Enum for the QuoteCharacter property."""

        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        read_single = "read_single"
        read_raw = "read_raw"
        read_raw_multiple_wildcard = "read_raw_multiple_wildcard"
        read_multiple_regex = "read_multiple_regex"
        read_multiple_wildcard = "read_multiple_wildcard"

    class RowDelimiter(Enum):
        """Enum for the RowDelimiter property."""

        question = "<?>"
        new_line = "new_line"
        carriage_return = "carriage_return"
        carriage_return_line_feed = "carriage_return_line_feed"
        line_feed = "line_feed"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class CodecAvro(Enum):
        """Enum for the CodecAvro property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        null = "null"
        snappy = "snappy"

    class CodecCsv(Enum):
        """Enum for the CodecCsv property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecDelimited(Enum):
        """Enum for the CodecDelimited property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecOrc(Enum):
        """Enum for the CodecOrc property."""

        lz4 = "lz4"
        lzo = "lzo"
        none = "none"
        snappy = "snappy"
        zlib = "zlib"

    class CodecParquet(Enum):
        """Enum for the CodecParquet property."""

        gzip = "gzip"
        uncompressed = "uncompressed"
        snappy = "snappy"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        delete = "delete"
        write = "write"
        write_raw = "write_raw"


class PLANNING_ANALYTICS:
    """Enums for properties in the PLANNING_ANALYTICS stage."""

    class ConnectionMode(Enum):
        """Enum for the ConnectionMode property."""

        cube_name = "cube_name"
        mdx_statement = "mdx_statement"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_seq = "default_seq"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1


class DREMIO:
    """Enums for properties in the DREMIO stage."""

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        none = "none"
        row = "row"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"


class GOOGLE_LOOKER:
    """Enums for properties in the GOOGLE_LOOKER stage."""

    class FileFormat(Enum):
        """Enum for the FileFormat property."""

        csv = "csv"
        delimited = "delimited"
        excel = "excel"
        json = "json"

    class InvalidDataHandling(Enum):
        """Enum for the InvalidDataHandling property."""

        column = "column"
        fail = "fail"
        row = "row"

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        read_single = "read_single"
        read_raw = "read_raw"
        read_raw_multiple_wildcard = "read_raw_multiple_wildcard"
        read_multiple_regex = "read_multiple_regex"
        read_multiple_wildcard = "read_multiple_wildcard"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1


class TABLEAU:
    """Enums for properties in the TABLEAU stage."""

    class InvalidDataHandling(Enum):
        """Enum for the InvalidDataHandling property."""

        column = "column"
        fail = "fail"
        row = "row"

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        read_single = "read_single"
        read_raw = "read_raw"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1


class POSTGRESQL_IBMCLOUD:
    """Enums for properties in the POSTGRESQL_IBMCLOUD stage."""

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        call = "call"
        call_statement = "call_statement"
        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        block = "block"
        none = "none"
        random = "random"
        row = "row"

    class LookupType(Enum):
        """Enum for the LookupType property."""

        empty = "empty"
        pxbridge = "pxbridge"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        call = "call"
        call_statement = "call_statement"
        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class TERADATA:
    """Enums for properties in the TERADATA stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        call = "call"
        call_statement = "call_statement"
        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        block = "block"
        none = "none"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        call = "call"
        call_statement = "call_statement"
        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class MARIADB:
    """Enums for properties in the MARIADB stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        none = "none"
        random = "random"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        delete = "delete"
        delete_insert = "delete_insert"
        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class CLOUD_OBJECT_STORAGE:
    """Enums for properties in the CLOUD_OBJECT_STORAGE stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class EscapeCharacter(Enum):
        """Enum for the EscapeCharacter property."""

        question = "<?>"
        backslash = "backslash"
        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class FieldDelimiter(Enum):
        """Enum for the FieldDelimiter property."""

        question = "<?>"
        colon = "colon"
        comma = "comma"
        tab = "tab"

    class FileFormat(Enum):
        """Enum for the FileFormat property."""

        avro = "avro"
        csv = "csv"
        delimited = "delimited"
        excel = "excel"
        json = "json"
        orc = "orc"
        parquet = "parquet"
        sav = "sav"
        xml = "xml"
        sas = "sas"
        shp = "shp"

    class InvalidDataHandling(Enum):
        """Enum for the InvalidDataHandling property."""

        column = "column"
        fail = "fail"
        row = "row"

    class QuoteCharacter(Enum):
        """Enum for the QuoteCharacter property."""

        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        read_single = "read_single"
        read_raw = "read_raw"
        read_raw_multiple_wildcard = "read_raw_multiple_wildcard"
        read_multiple_regex = "read_multiple_regex"
        read_multiple_wildcard = "read_multiple_wildcard"

    class RowDelimiter(Enum):
        """Enum for the RowDelimiter property."""

        question = "<?>"
        new_line = "new_line"
        carriage_return = "carriage_return"
        carriage_return_line_feed = "carriage_return_line_feed"
        line_feed = "line_feed"

    class TableFormat(Enum):
        """Enum for the TableFormat property."""

        deltalake = "deltalake"
        file = "file"
        iceberg = "iceberg"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class CodecAvro(Enum):
        """Enum for the CodecAvro property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        null = "null"
        snappy = "snappy"

    class CodecCsv(Enum):
        """Enum for the CodecCsv property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecDelimited(Enum):
        """Enum for the CodecDelimited property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecOrc(Enum):
        """Enum for the CodecOrc property."""

        lz4 = "lz4"
        lzo = "lzo"
        none = "none"
        snappy = "snappy"
        zlib = "zlib"

    class CodecParquet(Enum):
        """Enum for the CodecParquet property."""

        gzip = "gzip"
        uncompressed = "uncompressed"
        snappy = "snappy"

    class StorageClass(Enum):
        """Enum for the StorageClass property."""

        cold_vault = "cold_vault"
        flex = "flex"
        standard = "standard"
        vault = "vault"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class TableDataFileCompressionCodec(Enum):
        """Enum for the TableDataFileCompressionCodec property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        gzip = "gzip"
        lz4 = "lz4"
        lzo = "lzo"
        uncompressed = "uncompressed"
        snappy = "snappy"
        zlib = "zlib"

    class TableDataFileFormat(Enum):
        """Enum for the TableDataFileFormat property."""

        avro = "avro"
        orc = "orc"
        parquet = "parquet"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        delete = "delete"
        write = "write"
        write_raw = "write_raw"


class APACHE_KAFKA:
    """Enums for properties in the APACHE_KAFKA stage."""

    class IsolationLevel(Enum):
        """Enum for the IsolationLevel property."""

        read_committed = "read_committed"
        read_uncommitted = "read_uncommitted"

    class KafkaClientLoggingLevel(Enum):
        """Enum for the KafkaClientLoggingLevel property."""

        debug = "debug"
        error = "error"
        fatal = "fatal"
        info = "info"
        off = "off"
        trace = "trace"
        warn = "warn"

    class KafkaWarningAndErrorLogs(Enum):
        """Enum for the KafkaWarningAndErrorLogs property."""

        keep_severity = "keep_severity"
        log_as_informational = "log_as_informational"
        log_as_warning = "log_as_warning"

    class KeySerializer(Enum):
        """Enum for the KeySerializer property."""

        avro = "avro"
        avro_to_json = "avro_to_json"
        byte = "byte"
        double = "double"
        integer = "integer"
        small_integer = "small_integer"
        string = "string"

    class ResetPolicy(Enum):
        """Enum for the ResetPolicy property."""

        earliest = "earliest"
        latest = "latest"

    class ValueSerializer(Enum):
        """Enum for the ValueSerializer property."""

        avro = "avro"
        avro_to_json = "avro_to_json"
        byte = "byte"
        double = "double"
        integer = "integer"
        small_integer = "small_integer"
        string = "string"

    class DSClientLoggingLevel(Enum):
        """Enum for the DSClientLoggingLevel property."""

        debug = "debug"
        error = "error"
        fatal = "fatal"
        info = "info"
        off = "off"
        trace = "trace"
        warn = "warn"

    class DSIsolationLevel(Enum):
        """Enum for the DSIsolationLevel property."""

        read_committed = "read_committed"
        read_uncommitted = "read_uncommitted"

    class DSKeySerializerType(Enum):
        """Enum for the DSKeySerializerType property."""

        avro = "avro"
        avro_to_json = "avro_to_json"
        byte = "byte"
        double = "double"
        integer = "integer"
        small_integer = "small_integer"
        string = "string"

    class DSResetPolicy(Enum):
        """Enum for the DSResetPolicy property."""

        earliest = "earliest"
        latest = "latest"

    class DSValueSerializerType(Enum):
        """Enum for the DSValueSerializerType property."""

        avro = "avro"
        avro_to_json = "avro_to_json"
        byte = "byte"
        double = "double"
        integer = "integer"
        small_integer = "small_integer"
        string = "string"

    class DSWarnAndErrorLog(Enum):
        """Enum for the DSWarnAndErrorLog property."""

        keep_severity = "keep_severity"
        log_as_informational = "log_as_informational"
        log_as_warning = "log_as_warning"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ConnSchemaRegistryAuthentication(Enum):
        """Enum for the ConnSchemaRegistryAuthentication property."""

        none = "none"
        reuse_sasl_credentials = "reuse_sasl_credentials"
        user_credentials = "user_credentials"

    class ConnSchemaRegistrySecure(Enum):
        """Enum for the ConnSchemaRegistrySecure property."""

        kerberos = "kerberos"
        none = "none"
        ssl = "ssl"
        reuse_ssl = "reuse_ssl"


class WATSONX_DATA:
    """Enums for properties in the WATSONX_DATA stage."""

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        create = "create"
        replace = "replace"
        truncate = "truncate"


class TERADATA_DATASTAGE:
    """Enums for properties in the TERADATA_DATASTAGE stage."""

    class SslModeSslProtocol(Enum):
        """Enum for the SslModeSslProtocol property."""

        TLS1_2 = "TLS1_2"

    class AccessMethod(Enum):
        """Enum for the AccessMethod property."""

        bulk = "bulk"
        immediate = "immediate"

    class Disconnect(Enum):
        """Enum for the Disconnect property."""

        never = "never"
        period_of_inactivity = "period_of_inactivity"

    class LookupType(Enum):
        """Enum for the LookupType property."""

        empty = "empty"
        pxbridge = "pxbridge"

    class ParallelSynchronizationSyncTableAction(Enum):
        """Enum for the ParallelSynchronizationSyncTableAction property."""

        append = "append"
        create = "create"
        replace = "replace"
        truncate = "truncate"

    class ParallelSynchronizationSyncTableCleanup(Enum):
        """Enum for the ParallelSynchronizationSyncTableCleanup property."""

        drop = "drop"
        keep = "keep"

    class ParallelSynchronizationSyncTableWriteMode(Enum):
        """Enum for the ParallelSynchronizationSyncTableWriteMode property."""

        delete_then_insert = "delete_then_insert"
        insert = "insert"

    class SessionIsolationLevel(Enum):
        """Enum for the SessionIsolationLevel property."""

        default = "default"
        read_committed = "read_committed"
        read_uncommitted = "read_uncommitted"
        repeatable_read = "repeatable_read"
        serializable = "serializable"

    class SessionSchemaReconciliationUnusedFieldAction(Enum):
        """Enum for the SessionSchemaReconciliationUnusedFieldAction property."""

        abort = "abort"
        drop = "drop"
        keep = "keep"
        warn = "warn"

    class SourceTemporalSupportTemporalColumns(Enum):
        """Enum for the SourceTemporalSupportTemporalColumns property."""

        bi_temporal = "bi-temporal"
        none = "none"
        transaction_time = "transaction_time"
        valid_time = "valid_time"

    class SourceTemporalSupportTransactionTimeQualifier(Enum):
        """Enum for the SourceTemporalSupportTransactionTimeQualifier property."""

        as_of = "as_of"
        current = "current"
        non_sequenced = "non-sequenced"
        none = "none"

    class SourceTemporalSupportValidTimeQualifier(Enum):
        """Enum for the SourceTemporalSupportValidTimeQualifier property."""

        as_of = "as_of"
        current = "current"
        non_sequenced = "non-sequenced"
        none = "none"
        sequenced = "sequenced"

    class TransactionEndOfWave(Enum):
        """Enum for the TransactionEndOfWave property."""

        after = "after"
        before = "before"
        none = "none"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class RecordOrdering(Enum):
        """Enum for the RecordOrdering property."""

        zero = 0
        one = 1
        two = 2

    class InputMethod(Enum):
        """Enum for the InputMethod property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class CredentialsInputMethodSsl(Enum):
        """Enum for the CredentialsInputMethodSsl property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class BulkAccessCleanupMode(Enum):
        """Enum for the BulkAccessCleanupMode property."""

        drop = "drop"
        keep = "keep"

    class BulkAccessErrorControlDuplicateInsertRows(Enum):
        """Enum for the BulkAccessErrorControlDuplicateInsertRows property."""

        default = "default"
        ignore = "ignore"
        reject = "reject"

    class BulkAccessErrorControlDuplicateUpdateRows(Enum):
        """Enum for the BulkAccessErrorControlDuplicateUpdateRows property."""

        default = "default"
        ignore = "ignore"
        reject = "reject"

    class BulkAccessErrorControlMissingDeleteRows(Enum):
        """Enum for the BulkAccessErrorControlMissingDeleteRows property."""

        default = "default"
        ignore = "ignore"
        reject = "reject"

    class BulkAccessErrorControlMissingUpdateRows(Enum):
        """Enum for the BulkAccessErrorControlMissingUpdateRows property."""

        default = "default"
        ignore = "ignore"
        reject = "reject"

    class BulkAccessLoadType(Enum):
        """Enum for the BulkAccessLoadType property."""

        load = "load"
        stream = "stream"
        update = "update"

    class BulkAccessStartMode(Enum):
        """Enum for the BulkAccessStartMode property."""

        auto = "auto"
        clean = "clean"
        restart = "restart"

    class BulkAccessStreamLoadRobust(Enum):
        """Enum for the BulkAccessStreamLoadRobust property."""

        no = "no"
        yes = "yes"

    class BulkAccessStreamLoadSerialize(Enum):
        """Enum for the BulkAccessStreamLoadSerialize property."""

        no = "no"
        yes = "yes"

    class ImmediateAccessBufferUsage(Enum):
        """Enum for the ImmediateAccessBufferUsage property."""

        separate = "separate"
        share = "share"

    class LoggingLogColumnValuesDelimiter(Enum):
        """Enum for the LoggingLogColumnValuesDelimiter property."""

        comma = "comma"
        newline = "newline"
        space = "space"
        tab = "tab"

    class SqlUserDefined(Enum):
        """Enum for the SqlUserDefined property."""

        file = "file"
        statements = "statements"

    class SqlUserDefinedRequestType(Enum):
        """Enum for the SqlUserDefinedRequestType property."""

        individual = "individual"
        multi_statement = "multi-statement"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        create = "create"
        replace = "replace"
        truncate = "truncate"

    class TableActionGenerateCreateStatementCreateTableOptionsAllowDuplicateRows(Enum):
        """Enum for the TableActionGenerateCreateStatementCreateTableOptionsAllowDuplicateRows property."""

        default = "default"
        no = "no"
        yes = "yes"

    class TableActionGenerateCreateStatementCreateTableOptionsMakeDuplicateCopies(Enum):
        """Enum for the TableActionGenerateCreateStatementCreateTableOptionsMakeDuplicateCopies property."""

        default = "default"
        no = "no"
        yes = "yes"

    class TableActionGenerateCreateStatementCreateTableOptionsPrimaryIndexType(Enum):
        """Enum for the TableActionGenerateCreateStatementCreateTableOptionsPrimaryIndexType property."""

        no_primary_index = "no_primary_index"
        non_unique = "non-unique"
        unique = "unique"

    class TableActionGenerateCreateStatementCreateTableOptionsTableFreeSpace(Enum):
        """Enum for the TableActionGenerateCreateStatementCreateTableOptionsTableFreeSpace property."""

        default = "default"
        yes = "yes"

    class TargetTemporalSupportTemporalColumns(Enum):
        """Enum for the TargetTemporalSupportTemporalColumns property."""

        bi_temporal = "bi-temporal"
        none = "none"
        transaction_time = "transaction_time"
        valid_time = "valid_time"

    class TargetTemporalSupportTemporalQualifier(Enum):
        """Enum for the TargetTemporalSupportTemporalQualifier property."""

        current_valid_time = "current_valid_time"
        non_sequenced_valid_time = "non-sequenced_valid_time"
        non_temporal = "non-temporal"
        none = "none"
        sequenced_valid_time = "sequenced_valid_time"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        delete = "delete"
        delete_then_insert = "delete_then_insert"
        insert = "insert"
        insert_then_update = "insert_then_update"
        update = "update"
        update_then_insert = "update_then_insert"
        user_defined_sql = "user-defined_sql"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class APACHE_HBASE:
    """Enums for properties in the APACHE_HBASE stage."""

    class LookupType(Enum):
        """Enum for the LookupType property."""

        empty = ""
        pxbridge = "pxbridge"

    class TypeOfRowKeysInTheTargetTable(Enum):
        """Enum for the TypeOfRowKeysInTheTargetTable property."""

        hexadecimal_strings_with_values_greater_than_zero = "hexadecimal_strings_with_values_greater_than_zero"
        numeric_strings_with_values_greater_than_zero = "numeric_strings_with_values_greater_than_zero"
        uniform_byte_arrays = "uniform_byte_arrays"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class HbaseWriteMode(Enum):
        """Enum for the HbaseWriteMode property."""

        append_qualifiers_values = "append_qualifiers_values"
        delete_qualifiers = "delete_qualifiers"
        delete_row = "delete_row"
        put = "put"


class BIGSQL:
    """Enums for properties in the BIGSQL stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        call = "call"
        call_statement = "call_statement"
        general = "general"
        select = "select"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class InputMethod(Enum):
        """Enum for the InputMethod property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class CredentialsInputMethodSsl(Enum):
        """Enum for the CredentialsInputMethodSsl property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        call = "call"
        call_statement = "call_statement"
        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class ORACLE:
    """Enums for properties in the ORACLE stage."""

    class NumberType(Enum):
        """Enum for the NumberType property."""

        double = "double"
        varchar = "varchar"

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        call = "call"
        call_statement = "call_statement"
        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        block = "block"
        none = "none"
        row = "row"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        call = "call"
        call_statement = "call_statement"
        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class AMAZONS3:
    """Enums for properties in the AMAZONS3 stage."""

    class DSFileFormat(Enum):
        """Enum for the DSFileFormat property."""

        amazon_redshift = "2"
        avro = "4"
        csv = "1"
        delimited = "0"
        parquet = "6"
        orc = "7"

    class DSFileFormatDelimitedSyntaxDataFormat(Enum):
        """Enum for the DSFileFormatDelimitedSyntaxDataFormat property."""

        binary = "1"
        test = "0"

    class DSFileFormatDelimitedSyntaxRecordDef(Enum):
        """Enum for the DSFileFormatDelimitedSyntaxRecordDef property."""

        source_file = "1"
        delimited_string = "2"
        delimited_string_file = "3"
        none = "0"
        schema_file = "4"

    class DSReadMode(Enum):
        """Enum for the DSReadMode property."""

        list_all_buckets = "2"
        list_files_in_bucket = "3"
        multiple_files = "1"
        single_file = "0"

    class DSRejectMode(Enum):
        """Enum for the DSRejectMode property."""

        cont = "0"
        fail = "1"
        reject = "2"

    class QuoteCharacter(Enum):
        """Enum for the QuoteCharacter property."""

        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class TableFormat(Enum):
        """Enum for the TableFormat property."""

        deltalake = "deltalake"
        file = "file"
        iceberg = "iceberg"

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class EscapeCharacter(Enum):
        """Enum for the EscapeCharacter property."""

        question = "<?>"
        backslash = "backslash"
        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class FieldDelimiter(Enum):
        """Enum for the FieldDelimiter property."""

        question = "<?>"
        colon = "colon"
        comma = "comma"
        tab = "tab"

    class FileFormat(Enum):
        """Enum for the FileFormat property."""

        avro = "avro"
        csv = "csv"
        delimited = "delimited"
        excel = "excel"
        json = "json"
        orc = "orc"
        parquet = "parquet"
        sav = "sav"
        xml = "xml"

    class InvalidDataHandling(Enum):
        """Enum for the InvalidDataHandling property."""

        column = "column"
        fail = "fail"
        row = "row"

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        read_single = "read_single"
        read_raw = "read_raw"
        read_raw_multiple_wildcard = "read_raw_multiple_wildcard"
        read_multiple_regex = "read_multiple_regex"
        read_multiple_wildcard = "read_multiple_wildcard"

    class RowDelimiter(Enum):
        """Enum for the RowDelimiter property."""

        question = "<?>"
        new_line = "new_line"
        carriage_return = "carriage_return"
        carriage_return_line_feed = "carriage_return_line_feed"
        line_feed = "line_feed"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class DSCodecAvro(Enum):
        """Enum for the DSCodecAvro property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        null = "null"
        snappy = "snappy"

    class DSCodecCsv(Enum):
        """Enum for the DSCodecCsv property."""

        gzip = "1"
        compressed = "0"

    class DSCodecDelimited(Enum):
        """Enum for the DSCodecDelimited property."""

        gzip = "1"
        compressed = "0"

    class DSFileAttributesEncryption(Enum):
        """Enum for the DSFileAttributesEncryption property."""

        aes_256 = "1"
        aws_kms = "2"
        none = "0"

    class DSFileAttributesLifeCycleRuleLCRuleFormat(Enum):
        """Enum for the DSFileAttributesLifeCycleRuleLCRuleFormat property."""

        days_from_creation = "0"
        specific_data = "1"

    class DSFileAttributesLifeCycleRuleLCRuleScope(Enum):
        """Enum for the DSFileAttributesLifeCycleRuleLCRuleScope property."""

        file = "0"
        folder = "1"

    class DSFileAttributesStorageClass(Enum):
        """Enum for the DSFileAttributesStorageClass property."""

        reduced_redundancy_class = "1"
        standard_class = "0"

    class DSFileExists(Enum):
        """Enum for the DSFileExists property."""

        no_overwrite = "1"
        fail = "2"
        overwrite = "0"

    class DSFileFormatORCTargetOrcCompress(Enum):
        """Enum for the DSFileFormatORCTargetOrcCompress property."""

        none = "0"
        gzip = "2"
        snappy = "1"

    class DSFileFormatParquetTargetParquetCompress(Enum):
        """Enum for the DSFileFormatParquetTargetParquetCompress property."""

        gzip = "2"
        lzo = "3"
        none = "0"
        snappy = "1"

    class DSWriteMode(Enum):
        """Enum for the DSWriteMode property."""

        delete = "1"
        write = "0"

    class CodecAvro(Enum):
        """Enum for the CodecAvro property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        null = "null"
        snappy = "snappy"

    class CodecCsv(Enum):
        """Enum for the CodecCsv property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecDelimited(Enum):
        """Enum for the CodecDelimited property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecOrc(Enum):
        """Enum for the CodecOrc property."""

        lz4 = "lz4"
        lzo = "lzo"
        none = "none"
        snappy = "snappy"
        zlib = "zlib"

    class CodecParquet(Enum):
        """Enum for the CodecParquet property."""

        gzip = "gzip"
        uncompressed = "uncompressed"
        snappy = "snappy"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class TableDataFileCompressionCodec(Enum):
        """Enum for the TableDataFileCompressionCodec property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        gzip = "gzip"
        lz4 = "lz4"
        lzo = "lzo"
        uncompressed = "uncompressed"
        snappy = "snappy"
        zlib = "zlib"

    class TableDataFileFormat(Enum):
        """Enum for the TableDataFileFormat property."""

        avro = "avro"
        orc = "orc"
        parquet = "parquet"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        delete = "delete"
        write = "write"
        write_raw = "write_raw"


class AZURE_COSMOS:
    """Enums for properties in the AZURE_COSMOS stage."""

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        read_single = "read_single"
        read_raw = "read_raw"
        read_raw_multiple_wildcard = "read_raw_multiple_wildcard"
        read_multiple_regex = "read_multiple_regex"
        read_multiple_wildcard = "read_multiple_wildcard"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class InputFormat(Enum):
        """Enum for the InputFormat property."""

        json = "json"
        relational = "relational"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        delete = "delete"
        write = "write"


class AZURE_DATABRICKS:
    """Enums for properties in the AZURE_DATABRICKS stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"


class CASSANDRA_DATASTAGE:
    """Enums for properties in the CASSANDRA_DATASTAGE stage."""

    class LookupType(Enum):
        """Enum for the LookupType property."""

        empty = ""
        pxbridge = "pxbridge"

    class ParallelReadStrategy(Enum):
        """Enum for the ParallelReadStrategy property."""

        equal_splitter = "equal_splitter"
        host_aware = "host_aware"

    class ReadConsistencyLevel(Enum):
        """Enum for the ReadConsistencyLevel property."""

        all_nodes = "all_nodes"
        each_data_center_quorum = "each_data_center_quorum"
        local_one = "local_one"
        local_quorum = "local_quorum"
        one_node = "one_node"
        quorum = "quorum"
        three_nodes = "three_nodes"
        two_nodes = "two_nodes"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ModificationType(Enum):
        """Enum for the ModificationType property."""

        delete_columns = "delete_columns"
        delete_entire_rows = "delete_entire_rows"
        insert = "insert"
        update = "update"

    class WriteConsistencyLevel(Enum):
        """Enum for the WriteConsistencyLevel property."""

        all_nodes = "all_nodes"
        any_node = "any_node"
        each_data_center_quorum = "each_data_center_quorum"
        local_one = "local_one"
        local_quorum = "local_quorum"
        one_node = "one_node"
        quorum = "quorum"
        three_nodes = "three_nodes"
        two_nodes = "two_nodes"


class HDFS_APACHE:
    """Enums for properties in the HDFS_APACHE stage."""

    class DSFileFormat(Enum):
        """Enum for the DSFileFormat property."""

        avro = "avro"
        comma_separated_value_csv = "comma-separated_value_csv"
        delimited = "delimited"
        implicit = "implicit"
        orc = "orc"
        parquet = "parquet"
        sequencefile = "sequencefile"

    class DSFileFormatDelimitedSyntaxQuotes(Enum):
        """Enum for the DSFileFormatDelimitedSyntaxQuotes property."""

        double = "double"
        none = "none"
        single = "single"

    class DSFileFormatDelimitedSyntaxRecordDef(Enum):
        """Enum for the DSFileFormatDelimitedSyntaxRecordDef property."""

        delimited_string = "delimited_string"
        delimited_string_in_a_file = "delimited_string_in_a_file"
        file_header = "file_header"
        infer_schema = "infer_schema"
        none = "none"
        schema_file = "schema_file"

    class DSFileFormatImplSyntaxBinary(Enum):
        """Enum for the DSFileFormatImplSyntaxBinary property."""

        binary = "binary"

    class DSFileFormatImplSyntaxRecordDef(Enum):
        """Enum for the DSFileFormatImplSyntaxRecordDef property."""

        delimited_string = "delimited_string"
        delimited_string_in_a_file = "delimited_string_in_a_file"
        file_header = "file_header"
        none = "none"
        schema_file = "schema_file"

    class DSReadMode(Enum):
        """Enum for the DSReadMode property."""

        read_multiple_files = "read_multiple_files"
        read_single_file = "read_single_file"

    class DSRejectMode(Enum):
        """Enum for the DSRejectMode property."""

        cont = "continue"
        fail = "fail"
        reject = "reject"

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class EscapeCharacter(Enum):
        """Enum for the EscapeCharacter property."""

        question = "<?>"
        backslash = "backslash"
        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class FieldDelimiter(Enum):
        """Enum for the FieldDelimiter property."""

        question = "<?>"
        colon = "colon"
        comma = "comma"
        tab = "tab"

    class FileFormat(Enum):
        """Enum for the FileFormat property."""

        avro = "avro"
        csv = "csv"
        delimited = "delimited"
        excel = "excel"
        json = "json"
        orc = "orc"
        parquet = "parquet"
        sav = "sav"
        xml = "xml"
        sas = "sas"
        shp = "shp"

    class InvalidDataHandling(Enum):
        """Enum for the InvalidDataHandling property."""

        column = "column"
        fail = "fail"
        row = "row"

    class QuoteCharacter(Enum):
        """Enum for the QuoteCharacter property."""

        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        read_single = "read_single"
        read_raw = "read_raw"
        read_raw_multiple_wildcard = "read_raw_multiple_wildcard"
        read_multiple_regex = "read_multiple_regex"
        read_multiple_wildcard = "read_multiple_wildcard"

    class RowDelimiter(Enum):
        """Enum for the RowDelimiter property."""

        question = "<?>"
        new_line = "new_line"
        carriage_return = "carriage_return"
        carriage_return_line_feed = "carriage_return_line_feed"
        line_feed = "line_feed"

    class TableFormat(Enum):
        """Enum for the TableFormat property."""

        deltalake = "deltalake"
        file = "file"
        iceberg = "iceberg"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class DSCreateHiveTableHiveTableType(Enum):
        """Enum for the DSCreateHiveTableHiveTableType property."""

        external = "external"
        internal = "internal"

    class DSCreateHiveTableUseStagingTableHiveTargetTablePropertiesHiveOrcCompress(Enum):
        """Enum for the DSCreateHiveTableUseStagingTableHiveTargetTablePropertiesHiveOrcCompress property."""

        none = "none"
        snappy = "snappy"
        zlib = "zlib"

    class DSCreateHiveTableUseStagingTableHiveTargetTablePropertiesHiveParquetCompress(Enum):
        """Enum for the DSCreateHiveTableUseStagingTableHiveTargetTablePropertiesHiveParquetCompress property."""

        gzip = "gzip"
        lzo = "lzo"
        none = "none"
        snappy = "snappy"

    class DSCreateHiveTableUseStagingTableHiveTargetTablePropertiesHiveTargetTableFormat(Enum):
        """Enum for the DSCreateHiveTableUseStagingTableHiveTargetTablePropertiesHiveTargetTableFormat property."""

        orc = "orc"
        parquet = "parquet"

    class DSCreateHiveTableUseStagingTableHiveTargetTablePropertiesHiveTargetTableType(Enum):
        """Enum for the DSCreateHiveTableUseStagingTableHiveTargetTablePropertiesHiveTargetTableType property."""

        external = "external"
        internal = "internal"

    class DSFileExists(Enum):
        """Enum for the DSFileExists property."""

        do_not_overwrite_file = "do_not_overwrite_file"
        fail = "fail"
        overwrite_file = "overwrite_file"

    class DSFileFormatAvroTargetAvroCodec(Enum):
        """Enum for the DSFileFormatAvroTargetAvroCodec property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        none = "none"
        snappy = "snappy"

    class DSFileFormatOrcTargetOrcCompress(Enum):
        """Enum for the DSFileFormatOrcTargetOrcCompress property."""

        none = "none"
        snappy = "snappy"
        zlib = "zlib"

    class DSFileFormatParquetTargetParquetCompress(Enum):
        """Enum for the DSFileFormatParquetTargetParquetCompress property."""

        gzip = "gzip"
        lzo = "lzo"
        none = "none"
        snappy = "snappy"

    class DSWriteMode(Enum):
        """Enum for the DSWriteMode property."""

        delete = "delete"
        write_multiple_files = "write_multiple_files"
        write_single_file = "write_single_file"

    class CodecAvro(Enum):
        """Enum for the CodecAvro property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        null = "null"
        snappy = "snappy"

    class CodecCsv(Enum):
        """Enum for the CodecCsv property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecDelimited(Enum):
        """Enum for the CodecDelimited property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecOrc(Enum):
        """Enum for the CodecOrc property."""

        none = "none"
        snappy = "snappy"
        zlib = "zlib"

    class CodecParquet(Enum):
        """Enum for the CodecParquet property."""

        none = "none"
        gzip = "gzip"
        lzo = "lzo"
        snappy = "snappy"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class TableDataFileCompressionCodec(Enum):
        """Enum for the TableDataFileCompressionCodec property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        gzip = "gzip"
        lz4 = "lz4"
        lzo = "lzo"
        uncompressed = "uncompressed"
        snappy = "snappy"
        zlib = "zlib"

    class TableDataFileFormat(Enum):
        """Enum for the TableDataFileFormat property."""

        avro = "avro"
        orc = "orc"
        parquet = "parquet"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        delete = "delete"
        write = "write"
        write_raw = "write_raw"


class AMAZON_REDSHIFT:
    """Enums for properties in the AMAZON_REDSHIFT stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        none = "none"
        random = "random"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        load = "load"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class SAPIQ:
    """Enums for properties in the SAPIQ stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"


class IMPALA:
    """Enums for properties in the IMPALA stage."""

    class DSEnablePartitionedReadsPartitionMethod(Enum):
        """Enum for the DSEnablePartitionedReadsPartitionMethod property."""

        _hive_partition = "_hive_partition"
        _minimum_and_maximum_range = "_minimum_and_maximum_range"
        _modulus = "_modulus"

    class DSReadMode(Enum):
        """Enum for the DSReadMode property."""

        _select = "_select"

    class DSSessionCharacterSetForNonUnicodeColumns(Enum):
        """Enum for the DSSessionCharacterSetForNonUnicodeColumns property."""

        _custom = "_custom"
        _default = "_default"

    class DSTransactionAutoCommitMode(Enum):
        """Enum for the DSTransactionAutoCommitMode property."""

        _disable = "_disable"
        _enable = "_enable"

    class DSTransactionEndOfWave(Enum):
        """Enum for the DSTransactionEndOfWave property."""

        _no = "_no"
        _yes = "_yes"

    class DSTransactionIsolationLevel(Enum):
        """Enum for the DSTransactionIsolationLevel property."""

        _default = "_default"
        _read_committed = "_read_committed"
        _repeatable_read = "_repeatable_read"
        _serializable = "_serializable"

    class LookupType(Enum):
        """Enum for the LookupType property."""

        empty = "empty"
        pxbridge = "pxbridge"

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        block = "block"
        none = "none"
        random = "random"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class DSRecordOrdering(Enum):
        """Enum for the DSRecordOrdering property."""

        zero = 0
        one = 1
        two = 2

    class DSTableAction(Enum):
        """Enum for the DSTableAction property."""

        _append = "_append"
        _create = "_create"
        _replace = "_replace"
        _truncate = "_truncate"

    class DSTableActionGenerateCreateStatementRowFormat(Enum):
        """Enum for the DSTableActionGenerateCreateStatementRowFormat property."""

        _delimited = "_delimited"
        _ser_de = "_ser_de"
        _storage_format = "_storage_format"

    class DSTableActionGenerateCreateStatementStorageFormat(Enum):
        """Enum for the DSTableActionGenerateCreateStatementStorageFormat property."""

        _avro = "_avro"
        _orc = "_orc"
        _parquet = "_parquet"
        _rc_file = "_rc_file"
        _sequence_file = "_sequence_file"
        _text_file = "_text_file"

    class DSWriteMode(Enum):
        """Enum for the DSWriteMode property."""

        _custom = "_custom"
        _delete = "_delete"
        _insert = "_insert"
        _update = "_update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"


class DB2ZOS:
    """Enums for properties in the DB2ZOS stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        call = "call"
        call_statement = "call_statement"
        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        none = "none"
        random = "random"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class InputMethod(Enum):
        """Enum for the InputMethod property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class CredentialsInputMethodSsl(Enum):
        """Enum for the CredentialsInputMethodSsl property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        call = "call"
        call_statement = "call_statement"
        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class BIGQUERY:
    """Enums for properties in the BIGQUERY stage."""

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        call_statement = "call_statement"
        general = "general"
        select = "select"

    class LookupType(Enum):
        """Enum for the LookupType property."""

        empty = "empty"
        pxbridge = "pxbridge"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class FileFormat(Enum):
        """Enum for the FileFormat property."""

        avro = "avro"
        csv = "csv"
        orc = "orc"
        parquet = "parquet"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        call_statement = "call_statement"
        delete = "delete"
        delete_insert = "delete_insert"
        insert_only = "insert_only"
        merge = "merge"
        insert = "insert"
        update = "update"
        update_statement = "update_statement"


class INFORMIX:
    """Enums for properties in the INFORMIX stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        none = "none"
        random = "random"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class MapName(Enum):
        """Enum for the MapName property."""

        Adobe_Standard_Encoding = "Adobe-Standard-Encoding"
        ANSI_X3_4_1968 = "ANSI_X3.4-1968"
        ASCL_ASCII = "ASCL_ASCII"
        ASCL_ASCII_PC1 = "ASCL_ASCII-PC1"
        ASCL_BIG5 = "ASCL_BIG5"
        ASCL_C0_CONTROLS = "ASCL_C0-CONTROLS"
        ASCL_C1_CONTROLS = "ASCL_C1-CONTROLS"
        ASCL_EBCDIC = "ASCL_EBCDIC"
        ASCL_EBCDIC_037 = "ASCL_EBCDIC-037"
        ASCL_EBCDIC_1026 = "ASCL_EBCDIC-1026"
        ASCL_EBCDIC_500V1 = "ASCL_EBCDIC-500V1"
        ASCL_EBCDIC_875 = "ASCL_EBCDIC-875"
        ASCL_EBCDIC_CTRLS = "ASCL_EBCDIC-CTRLS"
        ASCL_EBCDIC_IBM1364 = "ASCL_EBCDIC-IBM1364"
        ASCL_EBCDIC_IBM1371 = "ASCL_EBCDIC-IBM1371"
        ASCL_EBCDIC_IBM933 = "ASCL_EBCDIC-IBM933"
        ASCL_EBCDIC_IBM937 = "ASCL_EBCDIC-IBM937"
        ASCL_EBCDIC_JP_CTRLS = "ASCL_EBCDIC-JP-CTRLS"
        ASCL_EBCDIC_JP_KANA = "ASCL_EBCDIC-JP-KANA"
        ASCL_EBCDIC_JP_KANA_E = "ASCL_EBCDIC-JP-KANA-E"
        ASCL_EBCDIC_JP_KANA_HW = "ASCL_EBCDIC-JP-KANA-HW"
        ASCL_GB2312 = "ASCL_GB2312"
        ASCL_ISO8859_1 = "ASCL_ISO8859-1"
        ASCL_ISO8859_10 = "ASCL_ISO8859-10"
        ASCL_ISO8859_15 = "ASCL_ISO8859-15"
        ASCL_ISO8859_2 = "ASCL_ISO8859-2"
        ASCL_ISO8859_3 = "ASCL_ISO8859-3"
        ASCL_ISO8859_4 = "ASCL_ISO8859-4"
        ASCL_ISO8859_5 = "ASCL_ISO8859-5"
        ASCL_ISO8859_6 = "ASCL_ISO8859-6"
        ASCL_ISO8859_7 = "ASCL_ISO8859-7"
        ASCL_ISO8859_8 = "ASCL_ISO8859-8"
        ASCL_ISO8859_9 = "ASCL_ISO8859-9"
        ASCL_JIS_EUC = "ASCL_JIS-EUC"
        ASCL_JIS_EUC_HWK = "ASCL_JIS-EUC-HWK"
        ASCL_JIS_EUC_P = "ASCL_JIS-EUC-P"
        ASCL_JIS_ROMAN = "ASCL_JIS-ROMAN"
        ASCL_JISX0201 = "ASCL_JISX0201"
        ASCL_JPN_EBCDIC = "ASCL_JPN-EBCDIC"
        ASCL_JPN_EBCDIK = "ASCL_JPN-EBCDIK"
        ASCL_JPN_EBCDIKC_CTRL = "ASCL_JPN-EBCDIKC-CTRL"
        ASCL_JPN_EUC = "ASCL_JPN-EUC"
        ASCL_JPN_EUC_KAT = "ASCL_JPN-EUC-KAT"
        ASCL_JPN_EUC_ONE = "ASCL_JPN-EUC-ONE"
        ASCL_JPN_EUC_RTE = "ASCL_JPN-EUC-RTE"
        ASCL_JPN_EUC_TWO = "ASCL_JPN-EUC-TWO"
        ASCL_JPN_IBM78 = "ASCL_JPN-IBM78"
        ASCL_JPN_IBM83 = "ASCL_JPN-IBM83"
        ASCL_JPN_JEF78 = "ASCL_JPN-JEF78"
        ASCL_JPN_JEF83 = "ASCL_JPN-JEF83"
        ASCL_JPN_JIPSE = "ASCL_JPN-JIPSE"
        ASCL_JPN_JIPSJ = "ASCL_JPN-JIPSJ"
        ASCL_JPN_JIS_RTE = "ASCL_JPN-JIS-RTE"
        ASCL_JPN_JIS8 = "ASCL_JPN-JIS8"
        ASCL_JPN_JIS8EUC_CTRL = "ASCL_JPN-JIS8EUC-CTRL"
        ASCL_JPN_KEIS_RTE = "ASCL_JPN-KEIS-RTE"
        ASCL_JPN_KEIS78 = "ASCL_JPN-KEIS78"
        ASCL_JPN_KEIS83 = "ASCL_JPN-KEIS83"
        ASCL_JPN_NEBCDIK = "ASCL_JPN-NEBCDIK"
        ASCL_JPN_SJIS = "ASCL_JPN-SJIS"
        ASCL_KOI8_R = "ASCL_KOI8-R"
        ASCL_KSC5601 = "ASCL_KSC5601"
        ASCL_KSC5601_1992 = "ASCL_KSC5601-1992"
        ASCL_MAC_GREEK = "ASCL_MAC-GREEK"
        ASCL_MAC_GREEK2 = "ASCL_MAC-GREEK2"
        ASCL_MAC_ROMAN = "ASCL_MAC-ROMAN"
        ASCL_MNEMONICS = "ASCL_MNEMONICS"
        ASCL_MS1250 = "ASCL_MS1250"
        ASCL_MS1251 = "ASCL_MS1251"
        ASCL_MS1252 = "ASCL_MS1252"
        ASCL_MS1253 = "ASCL_MS1253"
        ASCL_MS1254 = "ASCL_MS1254"
        ASCL_MS1255 = "ASCL_MS1255"
        ASCL_MS1256 = "ASCL_MS1256"
        ASCL_MS932 = "ASCL_MS932"
        ASCL_MS932_BASE = "ASCL_MS932-BASE"
        ASCL_MS932_EXTRA = "ASCL_MS932-EXTRA"
        ASCL_MS936 = "ASCL_MS936"
        ASCL_MS936_BASE = "ASCL_MS936-BASE"
        ASCL_MS949 = "ASCL_MS949"
        ASCL_MS950 = "ASCL_MS950"
        ASCL_MS950_BASE = "ASCL_MS950-BASE"
        ASCL_PC1040 = "ASCL_PC1040"
        ASCL_PC1041 = "ASCL_PC1041"
        ASCL_PC437 = "ASCL_PC437"
        ASCL_PC850 = "ASCL_PC850"
        ASCL_PC852 = "ASCL_PC852"
        ASCL_PC855 = "ASCL_PC855"
        ASCL_PC857 = "ASCL_PC857"
        ASCL_PC860 = "ASCL_PC860"
        ASCL_PC861 = "ASCL_PC861"
        ASCL_PC862 = "ASCL_PC862"
        ASCL_PC863 = "ASCL_PC863"
        ASCL_PC864 = "ASCL_PC864"
        ASCL_PC865 = "ASCL_PC865"
        ASCL_PC866 = "ASCL_PC866"
        ASCL_PC869 = "ASCL_PC869"
        ASCL_PC874 = "ASCL_PC874"
        ASCL_PRIME_SHIFT_JIS = "ASCL_PRIME-SHIFT-JIS"
        ASCL_SHIFT_JIS = "ASCL_SHIFT-JIS"
        ASCL_TAU_SHIFT_JIS = "ASCL_TAU-SHIFT-JIS"
        ASCL_TIS620 = "ASCL_TIS620"
        ASCL_TIS620_B = "ASCL_TIS620-B"
        Big5 = "Big5"
        Big5_HKSCS = "Big5-HKSCS"
        BOCU_1 = "BOCU-1"
        CESU_8 = "CESU-8"
        ebcdic_xml_us = "ebcdic-xml-us"
        EUC_KR = "EUC-KR"
        GB_2312_80 = "GB_2312-80"
        gb18030_gb18030 = "gb18030 gb18030"
        GB2312 = "GB2312"
        GBK = "GBK"
        hp_roman8 = "hp-roman8"
        HZ_HZ_GB_2312 = "HZ HZ-GB-2312"
        ibm_1006_P100_1995 = "ibm-1006_P100-1995"
        ibm_1025_P100_1995 = "ibm-1025_P100-1995"
        ibm_1026_P100_1995 = "ibm-1026_P100-1995"
        ibm_1047_P100_1995 = "ibm-1047_P100-1995"
        ibm_1047_P100_1995_swaplfnl = "ibm-1047_P100-1995,swaplfnl"
        ibm_1051_P100_1995 = "ibm-1051_P100-1995"
        ibm_1089_P100_1995 = "ibm-1089_P100-1995"
        ibm_1097_P100_1995 = "ibm-1097_P100-1995"
        ibm_1098_P100_1995 = "ibm-1098_P100-1995"
        ibm_1112_P100_1995 = "ibm-1112_P100-1995"
        ibm_1122_P100_1999 = "ibm-1122_P100-1999"
        ibm_1123_P100_1995 = "ibm-1123_P100-1995"
        ibm_1124_P100_1996 = "ibm-1124_P100-1996"
        ibm_1125_P100_1997 = "ibm-1125_P100-1997"
        ibm_1129_P100_1997 = "ibm-1129_P100-1997"
        ibm_1130_P100_1997 = "ibm-1130_P100-1997"
        ibm_1131_P100_1997 = "ibm-1131_P100-1997"
        ibm_1132_P100_1998 = "ibm-1132_P100-1998"
        ibm_1133_P100_1997 = "ibm-1133_P100-1997"
        ibm_1137_P100_1999 = "ibm-1137_P100-1999"
        ibm_1140_P100_1997 = "ibm-1140_P100-1997"
        ibm_1140_P100_1997_swaplfnl = "ibm-1140_P100-1997,swaplfnl"
        ibm_1141_P100_1997 = "ibm-1141_P100-1997"
        ibm_1141_P100_1997_swaplfnl = "ibm-1141_P100-1997,swaplfnl"
        ibm_1142_P100_1997 = "ibm-1142_P100-1997"
        ibm_1142_P100_1997_swaplfnl = "ibm-1142_P100-1997,swaplfnl"
        ibm_1143_P100_1997 = "ibm-1143_P100-1997"
        ibm_1143_P100_1997_swaplfnl = "ibm-1143_P100-1997,swaplfnl"
        ibm_1144_P100_1997 = "ibm-1144_P100-1997"
        ibm_1144_P100_1997_swaplfnl = "ibm-1144_P100-1997,swaplfnl"
        ibm_1145_P100_1997 = "ibm-1145_P100-1997"
        ibm_1145_P100_1997_swaplfnl = "ibm-1145_P100-1997,swaplfnl"
        ibm_1146_P100_1997 = "ibm-1146_P100-1997"
        ibm_1146_P100_1997_swaplfnl = "ibm-1146_P100-1997,swaplfnl"
        ibm_1147_P100_1997 = "ibm-1147_P100-1997"
        ibm_1147_P100_1997_swaplfnl = "ibm-1147_P100-1997,swaplfnl"
        ibm_1148_P100_1997 = "ibm-1148_P100-1997"
        ibm_1148_P100_1997_swaplfnl = "ibm-1148_P100-1997,swaplfnl"
        ibm_1149_P100_1997 = "ibm-1149_P100-1997"
        ibm_1149_P100_1997_swaplfnl = "ibm-1149_P100-1997,swaplfnl"
        ibm_1153_P100_1999 = "ibm-1153_P100-1999"
        ibm_1153_P100_1999_swaplfnl = "ibm-1153_P100-1999,swaplfnl"
        ibm_1154_P100_1999 = "ibm-1154_P100-1999"
        ibm_1155_P100_1999 = "ibm-1155_P100-1999"
        ibm_1156_P100_1999 = "ibm-1156_P100-1999"
        ibm_1157_P100_1999 = "ibm-1157_P100-1999"
        ibm_1158_P100_1999 = "ibm-1158_P100-1999"
        ibm_1160_P100_1999 = "ibm-1160_P100-1999"
        ibm_1162_P100_1999 = "ibm-1162_P100-1999"
        ibm_1164_P100_1999 = "ibm-1164_P100-1999"
        ibm_1168_P100_2002 = "ibm-1168_P100-2002"
        ibm_1250_P100_1995 = "ibm-1250_P100-1995"
        ibm_1251_P100_1995 = "ibm-1251_P100-1995"
        ibm_1252_P100_2000 = "ibm-1252_P100-2000"
        ibm_1253_P100_1995 = "ibm-1253_P100-1995"
        ibm_1254_P100_1995 = "ibm-1254_P100-1995"
        ibm_1255_P100_1995 = "ibm-1255_P100-1995"
        ibm_1256_P110_1997 = "ibm-1256_P110-1997"
        ibm_1257_P100_1995 = "ibm-1257_P100-1995"
        ibm_1258_P100_1997 = "ibm-1258_P100-1997"
        ibm_12712_P100_1998 = "ibm-12712_P100-1998"
        ibm_12712_P100_1998_swaplfnl = "ibm-12712_P100-1998,swaplfnl"
        ibm_1276_P100_1995 = "ibm-1276_P100-1995"
        ibm_1277_P100_1995 = "ibm-1277_P100-1995"
        ibm_1363_P110_1997 = "ibm-1363_P110-1997"
        ibm_1363_P11B_1998 = "ibm-1363_P11B-1998"
        ibm_1364_P110_1997 = "ibm-1364_P110-1997"
        ibm_1364_P110_2007 = "ibm-1364_P110-2007"
        ibm_1371_P100_1999 = "ibm-1371_P100-1999"
        ibm_1373_P100_2002 = "ibm-1373_P100-2002"
        ibm_1375_P100_2003 = "ibm-1375_P100-2003"
        ibm_1375_P100_2007 = "ibm-1375_P100-2007"
        ibm_1381_P110_1999 = "ibm-1381_P110-1999"
        ibm_1383_P110_1999 = "ibm-1383_P110-1999"
        ibm_1386_P100_2001 = "ibm-1386_P100-2001"
        ibm_1386_P100_2002 = "ibm-1386_P100-2002"
        ibm_1388_P103_2001 = "ibm-1388_P103-2001"
        ibm_1390_P110_2003 = "ibm-1390_P110-2003"
        ibm_1399_P110_2003 = "ibm-1399_P110-2003"
        ibm_16684_P110_2003 = "ibm-16684_P110-2003"
        ibm_16804_X110_1999 = "ibm-16804_X110-1999"
        ibm_16804_X110_1999_swaplfnl = "ibm-16804_X110-1999,swaplfnl"
        ibm_273_P100_1995 = "ibm-273_P100-1995"
        ibm_277_P100_1995 = "ibm-277_P100-1995"
        ibm_278_P100_1995 = "ibm-278_P100-1995"
        ibm_280_P100_1995 = "ibm-280_P100-1995"
        ibm_284_P100_1995 = "ibm-284_P100-1995"
        ibm_285_P100_1995 = "ibm-285_P100-1995"
        ibm_290_P100_1995 = "ibm-290_P100-1995"
        ibm_297_P100_1995 = "ibm-297_P100-1995"
        ibm_33722_P120_1999 = "ibm-33722_P120-1999"
        ibm_33722_P12A_P12A_2009_U2_Extended_UNIX_Code_Packed_Format_for_Japanese = (
            "ibm-33722_P12A_P12A-2009_U2 Extended_UNIX_Code_Packed_Format_for_Japanese"
        )
        ibm_33722_P12A_1999 = "ibm-33722_P12A-1999"
        ibm_367_P100_1995 = "ibm-367_P100-1995"
        ibm_37_P100_1995 = "ibm-37_P100-1995"
        ibm_37_P100_1995_swaplfnl = "ibm-37_P100-1995,swaplfnl"
        ibm_420_X120_1999 = "ibm-420_X120-1999"
        ibm_424_P100_1995 = "ibm-424_P100-1995"
        ibm_437_P100_1995 = "ibm-437_P100-1995"
        ibm_4517_P100_2005 = "ibm-4517_P100-2005"
        ibm_4899_P100_1998 = "ibm-4899_P100-1998"
        ibm_4909_P100_1999 = "ibm-4909_P100-1999"
        ibm_4971_P100_1999 = "ibm-4971_P100-1999"
        ibm_500_P100_1995 = "ibm-500_P100-1995"
        ibm_5012_P100_1999 = "ibm-5012_P100-1999"
        ibm_5123_P100_1999 = "ibm-5123_P100-1999"
        ibm_5346_P100_1998 = "ibm-5346_P100-1998"
        ibm_5347_P100_1998 = "ibm-5347_P100-1998"
        ibm_5348_P100_1997 = "ibm-5348_P100-1997"
        ibm_5349_P100_1998 = "ibm-5349_P100-1998"
        ibm_5350_P100_1998 = "ibm-5350_P100-1998"
        ibm_5351_P100_1998 = "ibm-5351_P100-1998"
        ibm_5352_P100_1998 = "ibm-5352_P100-1998"
        ibm_5353_P100_1998 = "ibm-5353_P100-1998"
        ibm_5354_P100_1998 = "ibm-5354_P100-1998"
        ibm_5471_P100_2006 = "ibm-5471_P100-2006"
        ibm_5478_P100_1995 = "ibm-5478_P100-1995"
        ibm_720_P100_1997 = "ibm-720_P100-1997"
        ibm_737_P100_1997 = "ibm-737_P100-1997"
        ibm_775_P100_1996 = "ibm-775_P100-1996"
        ibm_803_P100_1999 = "ibm-803_P100-1999"
        ibm_813_P100_1995 = "ibm-813_P100-1995"
        ibm_838_P100_1995 = "ibm-838_P100-1995"
        ibm_8482_P100_1999 = "ibm-8482_P100-1999"
        ibm_850_P100_1995 = "ibm-850_P100-1995"
        ibm_851_P100_1995 = "ibm-851_P100-1995"
        ibm_852_P100_1995 = "ibm-852_P100-1995"
        ibm_855_P100_1995 = "ibm-855_P100-1995"
        ibm_856_P100_1995 = "ibm-856_P100-1995"
        ibm_857_P100_1995 = "ibm-857_P100-1995"
        ibm_858_P100_1997 = "ibm-858_P100-1997"
        ibm_860_P100_1995 = "ibm-860_P100-1995"
        ibm_861_P100_1995 = "ibm-861_P100-1995"
        ibm_862_P100_1995 = "ibm-862_P100-1995"
        ibm_863_P100_1995 = "ibm-863_P100-1995"
        ibm_864_X110_1999 = "ibm-864_X110-1999"
        ibm_865_P100_1995 = "ibm-865_P100-1995"
        ibm_866_P100_1995 = "ibm-866_P100-1995"
        ibm_867_P100_1998 = "ibm-867_P100-1998"
        ibm_868_P100_1995 = "ibm-868_P100-1995"
        ibm_869_P100_1995 = "ibm-869_P100-1995"
        ibm_870_P100_1995 = "ibm-870_P100-1995"
        ibm_871_P100_1995 = "ibm-871_P100-1995"
        ibm_874_P100_1995 = "ibm-874_P100-1995"
        ibm_875_P100_1995 = "ibm-875_P100-1995"
        ibm_878_P100_1996 = "ibm-878_P100-1996"
        ibm_897_P100_1995 = "ibm-897_P100-1995"
        ibm_9005_X110_2007 = "ibm-9005_X110-2007"
        ibm_901_P100_1999 = "ibm-901_P100-1999"
        ibm_902_P100_1999 = "ibm-902_P100-1999"
        ibm_9067_X100_2005 = "ibm-9067_X100-2005"
        ibm_912_P100_1995 = "ibm-912_P100-1995"
        ibm_913_P100_2000 = "ibm-913_P100-2000"
        ibm_914_P100_1995 = "ibm-914_P100-1995"
        ibm_915_P100_1995 = "ibm-915_P100-1995"
        ibm_916_P100_1995 = "ibm-916_P100-1995"
        ibm_918_P100_1995 = "ibm-918_P100-1995"
        ibm_920_P100_1995 = "ibm-920_P100-1995"
        ibm_921_P100_1995 = "ibm-921_P100-1995"
        ibm_922_P100_1999 = "ibm-922_P100-1999"
        ibm_923_P100_1998 = "ibm-923_P100-1998"
        ibm_930_P120_1999 = "ibm-930_P120-1999"
        ibm_933_P110_1995 = "ibm-933_P110-1995"
        ibm_935_P110_1999 = "ibm-935_P110-1999"
        ibm_937_P110_1999 = "ibm-937_P110-1999"
        ibm_939_P120_1999 = "ibm-939_P120-1999"
        ibm_942_P12A_1999 = "ibm-942_P12A-1999"
        ibm_943_P130_1999 = "ibm-943_P130-1999"
        ibm_943_P15A_2003 = "ibm-943_P15A-2003"
        ibm_9447_P100_2002 = "ibm-9447_P100-2002"
        ibm_9448_X100_2005 = "ibm-9448_X100-2005"
        ibm_9449_P100_2002 = "ibm-9449_P100-2002"
        ibm_949_P110_1999 = "ibm-949_P110-1999"
        ibm_949_P11A_1999 = "ibm-949_P11A-1999"
        ibm_950_P110_1999 = "ibm-950_P110-1999"
        ibm_954_P101_2000 = "ibm-954_P101-2000"
        ibm_954_P101_2007 = "ibm-954_P101-2007"
        ibm_964_P110_1999 = "ibm-964_P110-1999"
        ibm_970_P110_P110_2006_U2 = "ibm-970_P110_P110-2006_U2"
        ibm_970_P110_1995 = "ibm-970_P110-1995"
        ibm_971_P100_1995 = "ibm-971_P100-1995"
        IBM_Thai = "IBM-Thai"
        IBM00858 = "IBM00858"
        IBM01140 = "IBM01140"
        IBM01141 = "IBM01141"
        IBM01142 = "IBM01142"
        IBM01143 = "IBM01143"
        IBM01144 = "IBM01144"
        IBM01145 = "IBM01145"
        IBM01146 = "IBM01146"
        IBM01147 = "IBM01147"
        IBM01148 = "IBM01148"
        IBM01149 = "IBM01149"
        IBM037 = "IBM037"
        IBM1026 = "IBM1026"
        IBM1047 = "IBM1047"
        IBM273 = "IBM273"
        IBM277 = "IBM277"
        IBM278 = "IBM278"
        IBM280 = "IBM280"
        IBM284 = "IBM284"
        IBM285 = "IBM285"
        IBM290 = "IBM290"
        IBM297 = "IBM297"
        IBM420 = "IBM420"
        IBM424 = "IBM424"
        IBM437 = "IBM437"
        IBM500 = "IBM500"
        IBM775 = "IBM775"
        IBM850 = "IBM850"
        IBM851 = "IBM851"
        IBM852 = "IBM852"
        IBM855 = "IBM855"
        IBM857 = "IBM857"
        IBM860 = "IBM860"
        IBM861 = "IBM861"
        IBM862 = "IBM862"
        IBM863 = "IBM863"
        IBM864 = "IBM864"
        IBM865 = "IBM865"
        IBM866 = "IBM866"
        IBM868 = "IBM868"
        IBM869 = "IBM869"
        IBM870 = "IBM870"
        IBM871 = "IBM871"
        IBM918 = "IBM918"
        IMAP_mailbox_name = "IMAP-mailbox-name"
        ISCII_version_0 = "ISCII,version=0"
        ISCII_version_1 = "ISCII,version=1"
        ISCII_version_2 = "ISCII,version=2"
        ISCII_version_3 = "ISCII,version=3"
        ISCII_version_4 = "ISCII,version=4"
        ISCII_version_5 = "ISCII,version=5"
        ISCII_version_6 = "ISCII,version=6"
        ISCII_version_7 = "ISCII,version=7"
        ISCII_version_8 = "ISCII,version=8"
        ISO_2022_locale_ja_version_0 = "ISO_2022,locale=ja,version=0"
        ISO_2022_locale_ja_version_1 = "ISO_2022,locale=ja,version=1"
        ISO_2022_locale_ja_version_2 = "ISO_2022,locale=ja,version=2"
        ISO_2022_locale_ja_version_3 = "ISO_2022,locale=ja,version=3"
        ISO_2022_locale_ja_version_4 = "ISO_2022,locale=ja,version=4"
        ISO_2022_locale_ko_version_0 = "ISO_2022,locale=ko,version=0"
        ISO_2022_locale_ko_version_1 = "ISO_2022,locale=ko,version=1"
        ISO_2022_locale_zh_version_0 = "ISO_2022,locale=zh,version=0"
        ISO_2022_locale_zh_version_1 = "ISO_2022,locale=zh,version=1"
        ISO_2022_locale_zh_version_2 = "ISO_2022,locale=zh,version=2"
        ISO_8859_1_1987 = "ISO_8859-1:1987"
        ISO_8859_2_1987 = "ISO_8859-2:1987"
        ISO_8859_3_1988 = "ISO_8859-3:1988"
        ISO_8859_4_1988 = "ISO_8859-4:1988"
        ISO_8859_5_1988 = "ISO_8859-5:1988"
        ISO_8859_6_1987 = "ISO_8859-6:1987"
        ISO_8859_7_1987 = "ISO_8859-7:1987"
        ISO_8859_8_1988 = "ISO_8859-8:1988"
        ISO_8859_9_1989 = "ISO_8859-9:1989"
        ISO_2022_CN = "ISO-2022-CN"
        ISO_2022_CN_EXT = "ISO-2022-CN-EXT"
        ISO_2022_JP = "ISO-2022-JP"
        ISO_2022_JP_2 = "ISO-2022-JP-2"
        ISO_2022_KR = "ISO-2022-KR"
        iso_8859_10_1998 = "iso-8859_10-1998"
        iso_8859_11_2001 = "iso-8859_11-2001"
        iso_8859_14_1998 = "iso-8859_14-1998"
        ISO_8859_1 = "ISO-8859-1"
        ISO_8859_10 = "ISO-8859-10"
        ISO_8859_13 = "ISO-8859-13"
        ISO_8859_14 = "ISO-8859-14"
        ISO_8859_15 = "ISO-8859-15"
        JIS_Encoding = "JIS_Encoding"
        KOI8_R = "KOI8-R"
        KOI8_U = "KOI8-U"
        KS_C_5601_1987 = "KS_C_5601-1987"
        LMBCS_1 = "LMBCS-1"
        macintosh = "macintosh"
        macos_0_2_10_2 = "macos-0_2-10.2"
        macos_2566_10_2 = "macos-2566-10.2"
        macos_29_10_2 = "macos-29-10.2"
        macos_35_10_2 = "macos-35-10.2"
        macos_6_2_10_4 = "macos-6_2-10.4"
        macos_6_10_2 = "macos-6-10.2"
        macos_7_3_10_2 = "macos-7_3-10.2"
        SCSU = "SCSU"
        Shift_JIS = "Shift_JIS"
        TIS_620 = "TIS-620"
        US_ASCII = "US-ASCII"
        UTF_16 = "UTF-16"
        UTF_16_version_1 = "UTF-16,version=1"
        UTF_16_version_2 = "UTF-16,version=2"
        UTF_16BE = "UTF-16BE"
        UTF_16BE_version_1 = "UTF-16BE,version=1"
        UTF_16LE = "UTF-16LE"
        UTF_16LE_version_1 = "UTF-16LE,version=1"
        UTF_32 = "UTF-32"
        UTF_32BE = "UTF-32BE"
        UTF_32LE = "UTF-32LE"
        UTF_7 = "UTF-7"
        UTF_8 = "UTF-8"
        UTF16_OppositeEndian = "UTF16_OppositeEndian"
        UTF16_PlatformEndian = "UTF16_PlatformEndian"
        UTF32_OppositeEndian = "UTF32_OppositeEndian"
        UTF32_PlatformEndian = "UTF32_PlatformEndian"
        windows_1250 = "windows-1250"
        windows_1251 = "windows-1251"
        windows_1252 = "windows-1252"
        windows_1253 = "windows-1253"
        windows_1254 = "windows-1254"
        windows_1255 = "windows-1255"
        windows_1256 = "windows-1256"
        windows_1256_2000 = "windows-1256-2000"
        windows_1257 = "windows-1257"
        windows_1258 = "windows-1258"
        windows_874_2000 = "windows-874-2000"
        windows_936_2000 = "windows-936-2000"
        windows_949_2000 = "windows-949-2000"
        windows_950_2000 = "windows-950-2000"
        x11_compound_text = "x11-compound-text"

    class AllowPerColumnMapping(Enum):
        """Enum for the AllowPerColumnMapping property."""

        false = "False"
        true = "True"

    class InputMethod(Enum):
        """Enum for the InputMethod property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class CredentialsInputMethodSsl(Enum):
        """Enum for the CredentialsInputMethodSsl property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class IBM_MQ:
    """Enums for properties in the IBM_MQ stage."""

    class AccessMode(Enum):
        """Enum for the AccessMode property."""

        as_in_queue_definition = "as_in_queue_definition"
        exclusive = "exclusive"
        exclusive_if_granted = "exclusive_if_granted"
        shared = "shared"

    class ErrorQueueContextMode(Enum):
        """Enum for the ErrorQueueContextMode property."""

        none = "none"
        set_all = "set_all"
        set_identity = "set_identity"

    class HeaderFieldsFilterFeedbackSystemValue(Enum):
        """Enum for the HeaderFieldsFilterFeedbackSystemValue property."""

        confirm_on_arrival = "confirm_on_arrival"
        confirm_on_delivery = "confirm_on_delivery"
        expiration = "expiration"
        message_too_big_for_queue_mqrc = "message_too_big_for_queue_mqrc"
        message_too_big_for_queue_manager_mqrc = "message_too_big_for_queue_manager_mqrc"
        negative_action_notification = "negative_action_notification"
        none = "none"
        not_authorized_mqrc = "not_authorized_mqrc"
        persistent_not_allowed_mqrc = "persistent_not_allowed_mqrc"
        positive_action_notification = "positive_action_notification"
        put_inhibited_mqrc = "put_inhibited_mqrc"
        queue_full_mqrc = "queue_full_mqrc"
        queue_space_not_available_mqrc = "queue_space_not_available_mqrc"
        quit = "quit"

    class HeaderFieldsFilterFormatSystemValue(Enum):
        """Enum for the HeaderFieldsFilterFormatSystemValue property."""

        mqadmin = "mqadmin"
        mqchcom = "mqchcom"
        mqcics = "mqcics"
        mqcmd1 = "mqcmd1"
        mqcmd2 = "mqcmd2"
        mqdead = "mqdead"
        mqevent = "mqevent"
        mqhdist = "mqhdist"
        mqhmde = "mqhmde"
        mqhref = "mqhref"
        mqhrf = "mqhrf"
        mqhrf2 = "mqhrf2"
        mqhwih = "mqhwih"
        mqims = "mqims"
        mqimsvs = "mqimsvs"
        mqnone = "mqnone"
        mqpcf = "mqpcf"
        mqstr = "mqstr"
        mqtrig = "mqtrig"
        mqxmit = "mqxmit"

    class HeaderFieldsFilterMsgFlagsValue(Enum):
        """Enum for the HeaderFieldsFilterMsgFlagsValue property."""

        last_message_in_group = "last_message_in_group"
        last_segment = "last_segment"
        message_in_group = "message_in_group"
        segment = "segment"
        segmentation_allowed = "segmentation_allowed"

    class HeaderFieldsFilterMsgTypeSystemValue(Enum):
        """Enum for the HeaderFieldsFilterMsgTypeSystemValue property."""

        datagram = "datagram"
        reply = "reply"
        report = "report"
        request = "request"

    class HeaderFieldsFilterPersistence(Enum):
        """Enum for the HeaderFieldsFilterPersistence property."""

        as_in_queue_definition = "as_in_queue_definition"
        not_persistent = "not_persistent"
        persistent = "persistent"

    class HeaderFieldsFilterPutApplTypeSystemValue(Enum):
        """Enum for the HeaderFieldsFilterPutApplTypeSystemValue property."""

        aix_unix = "aix,_unix"
        broker = "broker"
        channelinitiator = "channelinitiator"
        cics = "cics"
        cicsbridge = "cicsbridge"
        cicsvse = "cicsvse"
        dos = "dos"
        dqm = "dqm"
        guardian_nsk = "guardian,_nsk"
        ims = "ims"
        imsbridge = "imsbridge"
        java = "java"
        mvs_os390_zos = "mvs,_os390,_zos"
        nocontext = "nocontext"
        notesagent = "notesagent"
        os2 = "os2"
        os400 = "os400"
        qmgr = "qmgr"
        unknown = "unknown"
        user = "user"
        vms = "vms"
        vos = "vos"
        windows = "windows"
        windowsnt = "windowsnt"
        xcf = "xcf"

    class HeaderFieldsFilterReportValue(Enum):
        """Enum for the HeaderFieldsFilterReportValue property."""

        confirm_on_arrival = "confirm_on_arrival"
        confirm_on_arrival_with_data = "confirm_on_arrival_with_data"
        confirm_on_arrival_with_full_data = "confirm_on_arrival_with_full_data"
        confirm_on_delivery = "confirm_on_delivery"
        confirm_on_delivery_with_data = "confirm_on_delivery_with_data"
        confirm_on_delivery_with_full_data = "confirm_on_delivery_with_full_data"
        discard_message = "discard_message"
        exception = "exception"
        exception_with_data = "exception_with_data"
        exception_with_full_data = "exception_with_full_data"
        expiration = "expiration"
        expiration_with_data = "expiration_with_data"
        expiration_with_full_data = "expiration_with_full_data"
        negative_action_notification = "negative_action_notification"
        pass_correlation_id = "pass_correlation_id"
        pass_message_id = "pass_message_id"
        positive_action_notification = "positive_action_notification"

    class MessageOptionsMessageOrderAndAssembly(Enum):
        """Enum for the MessageOptionsMessageOrderAndAssembly property."""

        assemble_groups = "assemble_groups"
        assemble_logical_messages = "assemble_logical_messages"
        individual_ordered = "individual_ordered"
        individual_unordered = "individual_unordered"

    class MessageReadMode(Enum):
        """Enum for the MessageReadMode property."""

        delete = "delete"
        delete_under_transaction = "delete_under_transaction"
        keep = "keep"
        move_to_work_queue = "move_to_work_queue"

    class PubSubDeregistrationSubscriber(Enum):
        """Enum for the PubSubDeregistrationSubscriber property."""

        correlation_id_as_identity = "correlation_id_as_identity"
        deregister_all = "deregister_all"
        leave_only = "leave_only"
        variable_user_id = "variable_user_id"

    class PubSubRegistrationSubscriberGeneral(Enum):
        """Enum for the PubSubRegistrationSubscriberGeneral property."""

        anonymous = "anonymous"
        correlation_id_as_identity = "correlation_id_as_identity"
        duplicates_ok = "duplicates_ok"
        local = "local"
        new_publications_only = "new_publications_only"

    class PubSubRegistrationSubscriberIdentity(Enum):
        """Enum for the PubSubRegistrationSubscriberIdentity property."""

        add_name = "add_name"
        join_exclusive = "join_exclusive"
        join_shared = "join_shared"
        no_alteration = "no_alteration"
        variable_user_id = "variable_user_id"

    class PubSubRegistrationSubscriberPersistence(Enum):
        """Enum for the PubSubRegistrationSubscriberPersistence property."""

        non_persistent = "non_persistent"
        persistent = "persistent"
        persistent_as_publish = "persistent_as_publish"
        persistent_as_queue = "persistent_as_queue"

    class PubSubServiceType(Enum):
        """Enum for the PubSubServiceType property."""

        mqrfh = "mqrfh"
        mqrfh2 = "mqrfh2"

    class TransactionEndOfWave(Enum):
        """Enum for the TransactionEndOfWave property."""

        after = "after"
        before = "before"
        none = "none"

    class WorkQueueContextMode(Enum):
        """Enum for the WorkQueueContextMode property."""

        none = "none"
        set_all = "set_all"
        set_identity = "set_identity"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class RecordOrdering(Enum):
        """Enum for the RecordOrdering property."""

        zero = 0
        one = 1
        two = 2

    class ContextMode(Enum):
        """Enum for the ContextMode property."""

        none = "none"
        set_all = "set_all"
        set_identity = "set_identity"

    class HeaderFieldsSetterFeedbackSystemValue(Enum):
        """Enum for the HeaderFieldsSetterFeedbackSystemValue property."""

        confirm_on_arrival = "confirm_on_arrival"
        confirm_on_delivery = "confirm_on_delivery"
        expiration = "expiration"
        message_too_big_for_queue_mqrc = "message_too_big_for_queue_mqrc"
        message_too_big_for_queue_manager_mqrc = "message_too_big_for_queue_manager_mqrc"
        negative_action_notification = "negative_action_notification"
        none = "none"
        not_authorized_mqrc = "not_authorized_mqrc"
        persistent_not_allowed_mqrc = "persistent_not_allowed_mqrc"
        positive_action_notification = "positive_action_notification"
        put_inhibited_mqrc = "put_inhibited_mqrc"
        queue_full_mqrc = "queue_full_mqrc"
        queue_space_not_available_mqrc = "queue_space_not_available_mqrc"
        quit = "quit"

    class HeaderFieldsSetterFormatSystemValue(Enum):
        """Enum for the HeaderFieldsSetterFormatSystemValue property."""

        mqadmin = "mqadmin"
        mqchcom = "mqchcom"
        mqcics = "mqcics"
        mqcmd1 = "mqcmd1"
        mqcmd2 = "mqcmd2"
        mqdead = "mqdead"
        mqevent = "mqevent"
        mqhdist = "mqhdist"
        mqhmde = "mqhmde"
        mqhref = "mqhref"
        mqhrf = "mqhrf"
        mqhrf2 = "mqhrf2"
        mqhwih = "mqhwih"
        mqims = "mqims"
        mqimsvs = "mqimsvs"
        mqnone = "mqnone"
        mqpcf = "mqpcf"
        mqstr = "mqstr"
        mqtrig = "mqtrig"
        mqxmit = "mqxmit"

    class HeaderFieldsSetterMsgFlags(Enum):
        """Enum for the HeaderFieldsSetterMsgFlags property."""

        last_message_in_group = "last_message_in_group"
        last_segment = "last_segment"
        message_in_group = "message_in_group"
        segment = "segment"
        segmentation_allowed = "segmentation_allowed"

    class HeaderFieldsSetterMsgTypeSystemValue(Enum):
        """Enum for the HeaderFieldsSetterMsgTypeSystemValue property."""

        datagram = "datagram"
        reply = "reply"
        report = "report"
        request = "request"

    class HeaderFieldsSetterPersistence(Enum):
        """Enum for the HeaderFieldsSetterPersistence property."""

        as_in_queue_definition = "as_in_queue_definition"
        not_persistent = "not_persistent"
        persistent = "persistent"

    class HeaderFieldsSetterPutApplTypeSystemValue(Enum):
        """Enum for the HeaderFieldsSetterPutApplTypeSystemValue property."""

        aix_unix = "aix,_unix"
        broker = "broker"
        channelinitiator = "channelinitiator"
        cics = "cics"
        cicsbridge = "cicsbridge"
        cicsvse = "cicsvse"
        dos = "dos"
        dqm = "dqm"
        guardian_nsk = "guardian,_nsk"
        ims = "ims"
        imsbridge = "imsbridge"
        java = "java"
        mvs_os390_zos = "mvs,_os390,_zos"
        nocontext = "nocontext"
        notesagent = "notesagent"
        os2 = "os2"
        os400 = "os400"
        qmgr = "qmgr"
        unknown = "unknown"
        user = "user"
        vms = "vms"
        vos = "vos"
        windows = "windows"
        windowsnt = "windowsnt"
        xcf = "xcf"

    class HeaderFieldsSetterReport(Enum):
        """Enum for the HeaderFieldsSetterReport property."""

        confirm_on_arrival = "confirm_on_arrival"
        confirm_on_arrival_with_data = "confirm_on_arrival_with_data"
        confirm_on_arrival_with_full_data = "confirm_on_arrival_with_full_data"
        confirm_on_delivery = "confirm_on_delivery"
        confirm_on_delivery_with_data = "confirm_on_delivery_with_data"
        confirm_on_delivery_with_full_data = "confirm_on_delivery_with_full_data"
        discard_message = "discard_message"
        exception = "exception"
        exception_with_data = "exception_with_data"
        exception_with_full_data = "exception_with_full_data"
        expiration = "expiration"
        expiration_with_data = "expiration_with_data"
        expiration_with_full_data = "expiration_with_full_data"
        negative_action_notification = "negative_action_notification"
        pass_correlation_identifier = "pass_correlation_identifier"
        pass_message_identifier = "pass_message_identifier"
        positive_action_notification = "positive_action_notification"

    class HeaderFieldsSetterVersion(Enum):
        """Enum for the HeaderFieldsSetterVersion property."""

        one = "1"
        two = "2"

    class MessageWriteMode(Enum):
        """Enum for the MessageWriteMode property."""

        create = "create"
        create_under_transaction = "create_under_transaction"
        create_on_content = "create_on_content"
        create_on_content_under_transaction = "create_on_content_under_transaction"

    class OtherQueueSettingsClusterQueueBindingMode(Enum):
        """Enum for the OtherQueueSettingsClusterQueueBindingMode property."""

        as_in_queue_definition = "as_in_queue_definition"
        not_fixed = "not_fixed"
        on_open = "on_open"

    class OtherQueueSettingsDynamicQueueCloseOptions(Enum):
        """Enum for the OtherQueueSettingsDynamicQueueCloseOptions property."""

        delete = "delete"
        none = "none"
        purge_and_delete = "purge_and_delete"

    class PubSubDeregistrationPublisher(Enum):
        """Enum for the PubSubDeregistrationPublisher property."""

        correlation_id_as_identity = "correlation_id_as_identity"
        deregister_all = "deregister_all"

    class PubSubPublishMessageContentDescriptorMessageServiceDomain(Enum):
        """Enum for the PubSubPublishMessageContentDescriptorMessageServiceDomain property."""

        idoc = "idoc"
        mrm = "mrm"
        none = "none"
        xml = "xml"
        xmlns = "xmlns"

    class PubSubPublishPublication(Enum):
        """Enum for the PubSubPublishPublication property."""

        correlation_id_as_identity = "correlation_id_as_identity"
        no_registration = "no_registration"
        retain_publication = "retain_publication"

    class PubSubPublishPublicationFormatSystemValue(Enum):
        """Enum for the PubSubPublishPublicationFormatSystemValue property."""

        mqadmin = "mqadmin"
        mqchcom = "mqchcom"
        mqcics = "mqcics"
        mqcmd1 = "mqcmd1"
        mqcmd2 = "mqcmd2"
        mqdead = "mqdead"
        mqevent = "mqevent"
        mqhdist = "mqhdist"
        mqhmde = "mqhmde"
        mqhref = "mqhref"
        mqhrf = "mqhrf"
        mqhrf2 = "mqhrf2"
        mqhwih = "mqhwih"
        mqims = "mqims"
        mqimsvs = "mqimsvs"
        mqnone = "mqnone"
        mqpcf = "mqpcf"
        mqstr = "mqstr"
        mqtrig = "mqtrig"
        mqxmit = "mqxmit"

    class PubSubPublishRegistration(Enum):
        """Enum for the PubSubPublishRegistration property."""

        anonymous = "anonymous"
        correlation_id_as_identity = "correlation_id_as_identity"
        local = "local"

    class PubSubRegistrationPublisher(Enum):
        """Enum for the PubSubRegistrationPublisher property."""

        anonymous = "anonymous"
        correlation_id_as_identity = "correlation_id_as_identity"
        local = "local"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class JDBC:
    """Enums for properties in the JDBC stage."""

    class DSReadMode(Enum):
        """Enum for the DSReadMode property."""

        select = "select"

    class DSSessionCharacterSetForNonUnicodeColumns(Enum):
        """Enum for the DSSessionCharacterSetForNonUnicodeColumns property."""

        custom = "custom"
        default = "default"

    class DSTransactionAutocommitMode(Enum):
        """Enum for the DSTransactionAutocommitMode property."""

        disable = "disable"
        enable = "enable"

    class DSTransactionEndOfWave(Enum):
        """Enum for the DSTransactionEndOfWave property."""

        no = "no"
        yes = "yes"

    class DSTransactionIsolationLevel(Enum):
        """Enum for the DSTransactionIsolationLevel property."""

        default = "default"
        read_committed = "read_committed"
        read_uncommitted = "read_uncommitted"
        repeatable_read = "repeatable_read"
        serializable = "serializable"

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class DSRecordOrdering(Enum):
        """Enum for the DSRecordOrdering property."""

        zero = 0
        one = 1
        two = 2

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class DSTableAction(Enum):
        """Enum for the DSTableAction property."""

        append = "append"
        create = "create"
        replace = "replace"
        truncate = "truncate"

    class DSWriteMode(Enum):
        """Enum for the DSWriteMode property."""

        custom = "custom"
        delete = "delete"
        delete_then_insert = "delete_then_insert"
        insert = "insert"
        insert_new_rows_only = "insert_new_rows_only"
        insert_then_update = "insert_then_update"
        update = "update"
        update_then_insert = "update_then_insert"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class SAPIDOC:
    """Enums for properties in the SAPIDOC stage."""

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1


class DERBY:
    """Enums for properties in the DERBY stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class MINIO:
    """Enums for properties in the MINIO stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class EscapeCharacter(Enum):
        """Enum for the EscapeCharacter property."""

        question = "<?>"
        backslash = "backslash"
        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class FieldDelimiter(Enum):
        """Enum for the FieldDelimiter property."""

        question = "<?>"
        colon = "colon"
        comma = "comma"
        tab = "tab"

    class FileFormat(Enum):
        """Enum for the FileFormat property."""

        avro = "avro"
        csv = "csv"
        delimited = "delimited"
        excel = "excel"
        json = "json"
        orc = "orc"
        parquet = "parquet"
        sav = "sav"
        xml = "xml"
        sas = "sas"
        shp = "shp"

    class InvalidDataHandling(Enum):
        """Enum for the InvalidDataHandling property."""

        column = "column"
        fail = "fail"
        row = "row"

    class QuoteCharacter(Enum):
        """Enum for the QuoteCharacter property."""

        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        read_single = "read_single"
        read_raw = "read_raw"
        read_raw_multiple_wildcard = "read_raw_multiple_wildcard"
        read_multiple_regex = "read_multiple_regex"
        read_multiple_wildcard = "read_multiple_wildcard"

    class RowDelimiter(Enum):
        """Enum for the RowDelimiter property."""

        question = "<?>"
        new_line = "new_line"
        carriage_return = "carriage_return"
        carriage_return_line_feed = "carriage_return_line_feed"
        line_feed = "line_feed"

    class TableFormat(Enum):
        """Enum for the TableFormat property."""

        deltalake = "deltalake"
        file = "file"
        iceberg = "iceberg"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_seq = "default_seq"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class CodecAvro(Enum):
        """Enum for the CodecAvro property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        null = "null"
        snappy = "snappy"

    class CodecCsv(Enum):
        """Enum for the CodecCsv property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecDelimited(Enum):
        """Enum for the CodecDelimited property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecOrc(Enum):
        """Enum for the CodecOrc property."""

        lz4 = "lz4"
        lzo = "lzo"
        none = "none"
        snappy = "snappy"
        zlib = "zlib"

    class CodecParquet(Enum):
        """Enum for the CodecParquet property."""

        gzip = "gzip"
        uncompressed = "uncompressed"
        snappy = "snappy"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class TableDataFileCompressionCodec(Enum):
        """Enum for the TableDataFileCompressionCodec property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        gzip = "gzip"
        lz4 = "lz4"
        lzo = "lzo"
        uncompressed = "uncompressed"
        snappy = "snappy"
        zlib = "zlib"

    class TableDataFileFormat(Enum):
        """Enum for the TableDataFileFormat property."""

        avro = "avro"
        orc = "orc"
        parquet = "parquet"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        delete = "delete"
        write = "write"
        write_raw = "write_raw"


class EXASOL:
    """Enums for properties in the EXASOL stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"


class DB2WAREHOUSE:
    """Enums for properties in the DB2WAREHOUSE stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        call = "call"
        call_statement = "call_statement"
        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        block = "block"
        none = "none"
        random = "random"
        row = "row"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class InputMethod(Enum):
        """Enum for the InputMethod property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class CredentialsInputMethodSsl(Enum):
        """Enum for the CredentialsInputMethodSsl property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        call = "call"
        call_statement = "call_statement"
        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class MONGODB:
    """Enums for properties in the MONGODB stage."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        username_password = "username_password"

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"


class DVM:
    """Enums for properties in the DVM stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        general = "general"
        select = "select"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class GOOGLE_CLOUD_STORAGE:
    """Enums for properties in the GOOGLE_CLOUD_STORAGE stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class EscapeCharacter(Enum):
        """Enum for the EscapeCharacter property."""

        question = "<?>"
        backslash = "backslash"
        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class FieldDelimiter(Enum):
        """Enum for the FieldDelimiter property."""

        question = "<?>"
        colon = "colon"
        comma = "comma"
        tab = "tab"

    class FileFormat(Enum):
        """Enum for the FileFormat property."""

        avro = "avro"
        csv = "csv"
        delimited = "delimited"
        excel = "excel"
        json = "json"
        orc = "orc"
        parquet = "parquet"
        sav = "sav"
        xml = "xml"
        sas = "sas"
        shp = "shp"

    class InvalidDataHandling(Enum):
        """Enum for the InvalidDataHandling property."""

        column = "column"
        fail = "fail"
        reject = "reject"
        row = "row"

    class QuoteCharacter(Enum):
        """Enum for the QuoteCharacter property."""

        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        read_single = "read_single"
        read_raw = "read_raw"
        read_raw_multiple_wildcard = "read_raw_multiple_wildcard"
        read_multiple_regex = "read_multiple_regex"
        read_multiple_wildcard = "read_multiple_wildcard"

    class RowDelimiter(Enum):
        """Enum for the RowDelimiter property."""

        question = "<?>"
        new_line = "new_line"
        carriage_return = "carriage_return"
        carriage_return_line_feed = "carriage_return_line_feed"
        line_feed = "line_feed"

    class TableFormat(Enum):
        """Enum for the TableFormat property."""

        deltalake = "deltalake"
        file = "file"
        iceberg = "iceberg"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class CodecAvro(Enum):
        """Enum for the CodecAvro property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        null = "null"
        snappy = "snappy"

    class CodecCsv(Enum):
        """Enum for the CodecCsv property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecDelimited(Enum):
        """Enum for the CodecDelimited property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecOrc(Enum):
        """Enum for the CodecOrc property."""

        lz4 = "lz4"
        lzo = "lzo"
        none = "none"
        snappy = "snappy"
        zlib = "zlib"

    class CodecParquet(Enum):
        """Enum for the CodecParquet property."""

        gzip = "gzip"
        uncompressed = "uncompressed"
        snappy = "snappy"

    class StorageClass(Enum):
        """Enum for the StorageClass property."""

        coldline = "coldline"
        multi_regional = "multi_regional"
        nearline = "nearline"
        regional = "regional"
        standard = "standard"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class TableDataFileCompressionCodec(Enum):
        """Enum for the TableDataFileCompressionCodec property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        gzip = "gzip"
        lz4 = "lz4"
        lzo = "lzo"
        uncompressed = "uncompressed"
        snappy = "snappy"
        zlib = "zlib"

    class TableDataFileFormat(Enum):
        """Enum for the TableDataFileFormat property."""

        avro = "avro"
        orc = "orc"
        parquet = "parquet"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        delete = "delete"
        delete_multiple_prefix = "delete_multiple_prefix"
        write = "write"
        write_raw = "write_raw"


class ODBC:
    """Enums for properties in the ODBC stage."""

    class LogOnMech(Enum):
        """Enum for the LogOnMech property."""

        ldap = "ldap"
        td2 = "td2"

    class LookupType(Enum):
        """Enum for the LookupType property."""

        empty = "empty"
        pxbridge = "pxbridge"

    class SessionAutocommitMode(Enum):
        """Enum for the SessionAutocommitMode property."""

        off = "off"
        on = "on"

    class SessionCodePage(Enum):
        """Enum for the SessionCodePage property."""

        default = "default"
        unicode = "unicode"
        user_specified = "user-specified"

    class SessionIsolationLevel(Enum):
        """Enum for the SessionIsolationLevel property."""

        default = "default"
        read_committed = "read_committed"
        read_uncommitted = "read_uncommitted"
        repeatable_read = "repeatable_read"
        serializable = "serializable"

    class SqlEnablePartitioningPartitioningMethod(Enum):
        """Enum for the SqlEnablePartitioningPartitioningMethod property."""

        minimum_and_maximum_range = "minimum_and_maximum_range"
        modulus = "modulus"

    class TransactionEndOfWave(Enum):
        """Enum for the TransactionEndOfWave property."""

        after = "after"
        before = "before"
        none = "none"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class DSRecordOrdering(Enum):
        """Enum for the DSRecordOrdering property."""

        zero = 0
        one = 1
        two = 2

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class LoggingLogColumnValuesDelimiter(Enum):
        """Enum for the LoggingLogColumnValuesDelimiter property."""

        comma = "comma"
        newline = "newline"
        space = "space"
        tab = "tab"

    class SqlUserDefinedSql(Enum):
        """Enum for the SqlUserDefinedSql property."""

        file = "file"
        statements = "statements"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        create = "create"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        delete = "delete"
        delete_then_insert = "delete_then_insert"
        insert = "insert"
        insert_new_rows_only = "insert_new_rows_only"
        insert_then_update = "insert_then_update"
        update = "update"
        update_then_insert = "update_then_insert"
        user_defined_sql = "user-defined_sql"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class HTTP:
    """Enums for properties in the HTTP stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class EscapeCharacter(Enum):
        """Enum for the EscapeCharacter property."""

        question = "<?>"
        backslash = "backslash"
        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class FieldDelimiter(Enum):
        """Enum for the FieldDelimiter property."""

        question = "<?>"
        colon = "colon"
        comma = "comma"
        tab = "tab"

    class FileFormat(Enum):
        """Enum for the FileFormat property."""

        avro = "avro"
        csv = "csv"
        delimited = "delimited"
        excel = "excel"
        json = "json"
        orc = "orc"
        parquet = "parquet"
        sas = "sas"
        sav = "sav"
        shp = "shp"
        xml = "xml"

    class InvalidDataHandling(Enum):
        """Enum for the InvalidDataHandling property."""

        column = "column"
        fail = "fail"
        row = "row"

    class QuoteCharacter(Enum):
        """Enum for the QuoteCharacter property."""

        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        read_single = "read_single"
        read_raw = "read_raw"

    class RowDelimiter(Enum):
        """Enum for the RowDelimiter property."""

        question = "<?>"
        new_line = "new_line"
        carriage_return = "carriage_return"
        carriage_return_line_feed = "carriage_return_line_feed"
        line_feed = "line_feed"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1


class DV:
    """Enums for properties in the DV stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1


class CASSANDRA:
    """Enums for properties in the CASSANDRA stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class AZURE_POSTGRESQL:
    """Enums for properties in the AZURE_POSTGRESQL stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        call = "call"
        call_statement = "call_statement"
        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        block = "block"
        none = "none"
        random = "random"
        row = "row"

    class LookupType(Enum):
        """Enum for the LookupType property."""

        empty = "empty"
        pxbridge = "pxbridge"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        call = "call"
        call_statement = "call_statement"
        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class MYSQL:
    """Enums for properties in the MYSQL stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        call = "call"
        call_statement = "call_statement"
        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        none = "none"
        random = "random"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        call = "call"
        call_statement = "call_statement"
        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class SQLSERVER:
    """Enums for properties in the SQLSERVER stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        call = "call"
        call_statement = "call_statement"
        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        block = "block"
        none = "none"
        random = "random"
        row = "row"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        call = "call"
        call_statement = "call_statement"
        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class GREENPLUM:
    """Enums for properties in the GREENPLUM stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class AZUREDATALAKE:
    """Enums for properties in the AZUREDATALAKE stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class EscapeCharacter(Enum):
        """Enum for the EscapeCharacter property."""

        question = "<?>"
        backslash = "backslash"
        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class FieldDelimiter(Enum):
        """Enum for the FieldDelimiter property."""

        question = "<?>"
        colon = "colon"
        comma = "comma"
        tab = "tab"

    class FileFormat(Enum):
        """Enum for the FileFormat property."""

        avro = "avro"
        csv = "csv"
        delimited = "delimited"
        excel = "excel"
        json = "json"
        orc = "orc"
        parquet = "parquet"
        sav = "sav"
        xml = "xml"

    class InvalidDataHandling(Enum):
        """Enum for the InvalidDataHandling property."""

        column = "column"
        fail = "fail"
        row = "row"

    class QuoteCharacter(Enum):
        """Enum for the QuoteCharacter property."""

        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        read_single = "read_single"
        read_raw = "read_raw"
        read_raw_multiple_wildcard = "read_raw_multiple_wildcard"
        read_multiple_regex = "read_multiple_regex"
        read_multiple_wildcard = "read_multiple_wildcard"

    class RowDelimiter(Enum):
        """Enum for the RowDelimiter property."""

        question = "<?>"
        new_line = "new_line"
        carriage_return = "carriage_return"
        carriage_return_line_feed = "carriage_return_line_feed"
        line_feed = "line_feed"

    class TableFormat(Enum):
        """Enum for the TableFormat property."""

        deltalake = "deltalake"
        file = "file"
        iceberg = "iceberg"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class CodecAvro(Enum):
        """Enum for the CodecAvro property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        null = "null"
        snappy = "snappy"

    class CodecCsv(Enum):
        """Enum for the CodecCsv property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecDelimited(Enum):
        """Enum for the CodecDelimited property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecOrc(Enum):
        """Enum for the CodecOrc property."""

        lz4 = "lz4"
        lzo = "lzo"
        none = "none"
        snappy = "snappy"
        zlib = "zlib"

    class CodecParquet(Enum):
        """Enum for the CodecParquet property."""

        gzip = "gzip"
        uncompressed = "uncompressed"
        snappy = "snappy"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class TableDataFileCompressionCodec(Enum):
        """Enum for the TableDataFileCompressionCodec property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        gzip = "gzip"
        lz4 = "lz4"
        lzo = "lzo"
        uncompressed = "uncompressed"
        snappy = "snappy"
        zlib = "zlib"

    class TableDataFileFormat(Enum):
        """Enum for the TableDataFileFormat property."""

        avro = "avro"
        orc = "orc"
        parquet = "parquet"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        delete = "delete"
        write = "write"
        write_raw = "write_raw"


class GOOGLE_PUB_SUB:
    """Enums for properties in the GOOGLE_PUB_SUB stage."""

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1


class DENODO:
    """Enums for properties in the DENODO stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        update_statement = "update_statement"


class DROPBOX:
    """Enums for properties in the DROPBOX stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class EscapeCharacter(Enum):
        """Enum for the EscapeCharacter property."""

        question = "<?>"
        backslash = "backslash"
        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class FieldDelimiter(Enum):
        """Enum for the FieldDelimiter property."""

        question = "<?>"
        colon = "colon"
        comma = "comma"
        tab = "tab"

    class FileFormat(Enum):
        """Enum for the FileFormat property."""

        avro = "avro"
        csv = "csv"
        delimited = "delimited"
        excel = "excel"
        json = "json"
        orc = "orc"
        parquet = "parquet"
        sav = "sav"
        xml = "xml"
        sas = "sas"
        shp = "shp"

    class InvalidDataHandling(Enum):
        """Enum for the InvalidDataHandling property."""

        column = "column"
        fail = "fail"
        row = "row"

    class QuoteCharacter(Enum):
        """Enum for the QuoteCharacter property."""

        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        read_single = "read_single"
        read_raw = "read_raw"
        read_raw_multiple_wildcard = "read_raw_multiple_wildcard"
        read_multiple_regex = "read_multiple_regex"
        read_multiple_wildcard = "read_multiple_wildcard"

    class RowDelimiter(Enum):
        """Enum for the RowDelimiter property."""

        question = "<?>"
        new_line = "new_line"
        carriage_return = "carriage_return"
        carriage_return_line_feed = "carriage_return_line_feed"
        line_feed = "line_feed"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class CodecAvro(Enum):
        """Enum for the CodecAvro property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        null = "null"
        snappy = "snappy"

    class CodecCsv(Enum):
        """Enum for the CodecCsv property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecDelimited(Enum):
        """Enum for the CodecDelimited property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecOrc(Enum):
        """Enum for the CodecOrc property."""

        lz4 = "lz4"
        lzo = "lzo"
        none = "none"
        snappy = "snappy"
        zlib = "zlib"

    class CodecParquet(Enum):
        """Enum for the CodecParquet property."""

        gzip = "gzip"
        uncompressed = "uncompressed"
        snappy = "snappy"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        delete = "delete"
        write = "write"
        write_raw = "write_raw"


class SALESFORCE:
    """Enums for properties in the SALESFORCE stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"


class AZURESQL:
    """Enums for properties in the AZURESQL stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        call = "call"
        call_statement = "call_statement"
        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        block = "block"
        none = "none"
        random = "random"
        row = "row"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        call = "call"
        call_statement = "call_statement"
        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class DB2:
    """Enums for properties in the DB2 stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"
        call = "call"
        call_statement = "call_statement"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        block = "block"
        none = "none"
        random = "random"
        row = "row"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"
        call = "call"
        call_statement = "call_statement"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class InputMethod(Enum):
        """Enum for the InputMethod property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class CredentialsInputMethodSsl(Enum):
        """Enum for the CredentialsInputMethodSsl property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class STORAGE_VOLUME:
    """Enums for properties in the STORAGE_VOLUME stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class EscapeCharacter(Enum):
        """Enum for the EscapeCharacter property."""

        question = "<?>"
        backslash = "backslash"
        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class FieldDelimiter(Enum):
        """Enum for the FieldDelimiter property."""

        question = "<?>"
        colon = "colon"
        comma = "comma"
        tab = "tab"

    class FileFormat(Enum):
        """Enum for the FileFormat property."""

        avro = "avro"
        csv = "csv"
        delimited = "delimited"
        excel = "excel"
        json = "json"
        orc = "orc"
        parquet = "parquet"
        sav = "sav"
        xml = "xml"
        sas = "sas"
        shp = "shp"

    class InvalidDataHandling(Enum):
        """Enum for the InvalidDataHandling property."""

        column = "column"
        fail = "fail"
        row = "row"

    class QuoteCharacter(Enum):
        """Enum for the QuoteCharacter property."""

        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        read_single = "read_single"
        read_raw = "read_raw"
        read_raw_multiple_wildcard = "read_raw_multiple_wildcard"
        read_multiple_regex = "read_multiple_regex"
        read_multiple_wildcard = "read_multiple_wildcard"

    class RowDelimiter(Enum):
        """Enum for the RowDelimiter property."""

        question = "<?>"
        new_line = "new_line"
        carriage_return = "carriage_return"
        carriage_return_line_feed = "carriage_return_line_feed"
        line_feed = "line_feed"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class CodecAvro(Enum):
        """Enum for the CodecAvro property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        null = "null"
        snappy = "snappy"

    class CodecCsv(Enum):
        """Enum for the CodecCsv property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecDelimited(Enum):
        """Enum for the CodecDelimited property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecOrc(Enum):
        """Enum for the CodecOrc property."""

        lz4 = "lz4"
        lzo = "lzo"
        none = "none"
        snappy = "snappy"
        zlib = "zlib"

    class CodecParquet(Enum):
        """Enum for the CodecParquet property."""

        gzip = "gzip"
        uncompressed = "uncompressed"
        snappy = "snappy"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        delete = "delete"
        write = "write"
        write_raw = "write_raw"


class NETEZZA_OPTIMIZED:
    """Enums for properties in the NETEZZA_OPTIMIZED stage."""

    class BeforeAfterSqlAfterSqlFailOnErrorLogLevelForAfterSql(Enum):
        """Enum for the BeforeAfterSqlAfterSqlFailOnErrorLogLevelForAfterSql property."""

        info = "info"
        none = "none"
        warning = "warning"

    class BeforeAfterSqlAfterSqlNodeFailOnErrorLogLevelForAfterSqlNode(Enum):
        """Enum for the BeforeAfterSqlAfterSqlNodeFailOnErrorLogLevelForAfterSqlNode property."""

        info = "info"
        none = "none"
        warning = "warning"

    class BeforeAfterSqlBeforeSqlFailOnErrorLogLevelForBeforeSql(Enum):
        """Enum for the BeforeAfterSqlBeforeSqlFailOnErrorLogLevelForBeforeSql property."""

        info = "info"
        none = "none"
        warning = "warning"

    class BeforeAfterSqlBeforeSqlNodeFailOnErrorLogLevelForBeforeSqlNode(Enum):
        """Enum for the BeforeAfterSqlBeforeSqlNodeFailOnErrorLogLevelForBeforeSqlNode property."""

        info = "info"
        none = "none"
        warning = "warning"

    class LookupType(Enum):
        """Enum for the LookupType property."""

        empty = ""
        pxbridge = "pxbridge"
        normal_1a = r"normal\(1a)"

    class SessionSchemaReconciliationMismatchReportingAction(Enum):
        """Enum for the SessionSchemaReconciliationMismatchReportingAction property."""

        info = "info"
        none = "none"
        warning = "warning"

    class SessionSchemaReconciliationMismatchReportingActionSource(Enum):
        """Enum for the SessionSchemaReconciliationMismatchReportingActionSource property."""

        info = "info"
        none = "none"
        warning = "warning"

    class SessionSchemaReconciliationTypeMismatchAction(Enum):
        """Enum for the SessionSchemaReconciliationTypeMismatchAction property."""

        drop = "drop"
        fail = "fail"
        keep = "keep"

    class SessionSchemaReconciliationTypeMismatchActionSource(Enum):
        """Enum for the SessionSchemaReconciliationTypeMismatchActionSource property."""

        drop = "drop"
        fail = "fail"
        keep = "keep"

    class SessionSchemaReconciliationUnmatchedLinkColumnActionRequestInputLink(Enum):
        """Enum for the SessionSchemaReconciliationUnmatchedLinkColumnActionRequestInputLink property."""

        drop = "drop"
        fail = "fail"

    class SessionSchemaReconciliationUnmatchedLinkColumnActionSource(Enum):
        """Enum for the SessionSchemaReconciliationUnmatchedLinkColumnActionSource property."""

        drop = "drop"
        fail = "fail"

    class SessionSchemaReconciliationUnmatchedTableOrQueryColumnActionRequest(Enum):
        """Enum for the SessionSchemaReconciliationUnmatchedTableOrQueryColumnActionRequest property."""

        fail = "fail"
        ignore = "ignore"

    class SessionSchemaReconciliationUnmatchedTableOrQueryColumnActionSource(Enum):
        """Enum for the SessionSchemaReconciliationUnmatchedTableOrQueryColumnActionSource property."""

        fail = "fail"
        ignore = "ignore"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class SessionLoadOptionsGenerateStatisticsGenerateStatisticsMode(Enum):
        """Enum for the SessionLoadOptionsGenerateStatisticsGenerateStatisticsMode property."""

        database = "database"
        table = "table"

    class SessionSchemaReconciliationUnmatchedLinkColumnAction(Enum):
        """Enum for the SessionSchemaReconciliationUnmatchedLinkColumnAction property."""

        drop = "drop"
        fail = "fail"
        keep = "keep"

    class SessionSchemaReconciliationUnmatchedTableColumnAction(Enum):
        """Enum for the SessionSchemaReconciliationUnmatchedTableColumnAction property."""

        fail = "fail"
        ignore_all = "ignore_all"
        ignore_nullable = "ignore_nullable"

    class SessionTemporaryWorkTable(Enum):
        """Enum for the SessionTemporaryWorkTable property."""

        automatic = "automatic"
        existing = "existing"
        user_defined = "user-defined"

    class SessionTemporaryWorkTableEnableMergeJoin(Enum):
        """Enum for the SessionTemporaryWorkTableEnableMergeJoin property."""

        database_default = "database_default"
        no = "no"
        yes = "yes"

    class SqlCheckDuplicateRowsDuplicateRowAction(Enum):
        """Enum for the SqlCheckDuplicateRowsDuplicateRowAction property."""

        fail = "fail"
        filter = "filter"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        create = "create"
        replace = "replace"
        truncate = "truncate"

    class TableActionGenerateCreateStatementDistributionKey(Enum):
        """Enum for the TableActionGenerateCreateStatementDistributionKey property."""

        automatic = "automatic"
        random = "random"
        user_defined = "user-defined"

    class TableActionGenerateCreateStatementFailOnErrorLogLevelForCreateStatement(Enum):
        """Enum for the TableActionGenerateCreateStatementFailOnErrorLogLevelForCreateStatement property."""

        info = "info"
        none = "none"
        warning = "warning"

    class TableActionGenerateDropStatementFailOnErrorLogLevelForDropStatement(Enum):
        """Enum for the TableActionGenerateDropStatementFailOnErrorLogLevelForDropStatement property."""

        info = "info"
        none = "none"
        warning = "warning"

    class TableActionGenerateTruncateStatementFailOnErrorLogLevelForTruncateStatement(Enum):
        """Enum for the TableActionGenerateTruncateStatementFailOnErrorLogLevelForTruncateStatement property."""

        info = "info"
        none = "none"
        warning = "warning"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        action_column = "action_column"
        delete = "delete"
        delete_then_insert = "delete_then_insert"
        insert = "insert"
        update = "update"
        update_then_insert = "update_then_insert"
        user_defined_sql = "user-defined_sql"


class APACHE_HIVE:
    """Enums for properties in the APACHE_HIVE stage."""

    class DSEnablePartitionedReadsPartitionMethod(Enum):
        """Enum for the DSEnablePartitionedReadsPartitionMethod property."""

        _hive_partition = "_hive_partition"
        _minimum_and_maximum_range = "_minimum_and_maximum_range"
        _modulus = "_modulus"

    class DSReadMode(Enum):
        """Enum for the DSReadMode property."""

        _select = "_select"

    class DSSessionCharacterSetForNonUnicodeColumns(Enum):
        """Enum for the DSSessionCharacterSetForNonUnicodeColumns property."""

        _custom = "_custom"
        _default = "_default"

    class DSTransactionAutoCommitMode(Enum):
        """Enum for the DSTransactionAutoCommitMode property."""

        _disable = "_disable"
        _enable = "_enable"

    class DSTransactionEndOfWave(Enum):
        """Enum for the DSTransactionEndOfWave property."""

        _no = "_no"
        _yes = "_yes"

    class DSTransactionIsolationLevel(Enum):
        """Enum for the DSTransactionIsolationLevel property."""

        _default = "_default"
        _read_committed = "_read_committed"
        _repeatable_read = "_repeatable_read"
        _serializable = "_serializable"

    class LookupType(Enum):
        """Enum for the LookupType property."""

        empty = "empty"
        pxbridge = "pxbridge"

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        block = "block"
        none = "none"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class DSRecordOrdering(Enum):
        """Enum for the DSRecordOrdering property."""

        zero = 0
        one = 1
        two = 2

    class DSTableAction(Enum):
        """Enum for the DSTableAction property."""

        _append = "_append"
        _create = "_create"
        _replace = "_replace"
        _truncate = "_truncate"

    class DSTableActionGenerateCreateStatementRowFormat(Enum):
        """Enum for the DSTableActionGenerateCreateStatementRowFormat property."""

        _delimited = "_delimited"
        _ser_de = "_ser_de"
        _storage_format = "_storage_format"

    class DSTableActionGenerateCreateStatementStorageFormat(Enum):
        """Enum for the DSTableActionGenerateCreateStatementStorageFormat property."""

        _avro = "_avro"
        _orc = "_orc"
        _parquet = "_parquet"
        _rc_file = "_rc_file"
        _sequence_file = "_sequence_file"
        _text_file = "_text_file"

    class DSWriteMode(Enum):
        """Enum for the DSWriteMode property."""

        _custom = "_custom"
        _delete = "_delete"
        _insert = "_insert"
        _update = "_update"

    class EscapeCharacter(Enum):
        """Enum for the EscapeCharacter property."""

        question = "<?>"
        backslash = "backslash"
        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class FieldDelimiter(Enum):
        """Enum for the FieldDelimiter property."""

        question = "<?>"
        colon = "colon"
        comma = "comma"
        tab = "tab"

    class FileFormat(Enum):
        """Enum for the FileFormat property."""

        avro = "avro"
        csv = "csv"
        delimited = "delimited"
        orc = "orc"
        parquet = "parquet"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"


class SNOWFLAKE:
    """Enums for properties in the SNOWFLAKE stage."""

    class DSAutoCommitMode(Enum):
        """Enum for the DSAutoCommitMode property."""

        disable = "disable"
        enable = "enable"

    class DSEndOfWave(Enum):
        """Enum for the DSEndOfWave property."""

        _no = "_no"
        _yes = "_yes"

    class DSIsolationLevel(Enum):
        """Enum for the DSIsolationLevel property."""

        default = "default"
        read_committed = "read_committed"

    class DSSessionCharacterSetForNonUnicodeColumns(Enum):
        """Enum for the DSSessionCharacterSetForNonUnicodeColumns property."""

        _custom = "_custom"
        _default = "_default"

    class LookupType(Enum):
        """Enum for the LookupType property."""

        empty = "empty"
        pxbridge = "pxbridge"

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        call = "call"
        call_statement = "call_statement"
        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        block = "block"
        none = "none"
        random = "random"
        row = "row"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class DSRecordOrdering(Enum):
        """Enum for the DSRecordOrdering property."""

        zero = 0
        one = 1
        two = 2

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class DSLoadFromFileAzureEncryption(Enum):
        """Enum for the DSLoadFromFileAzureEncryption property."""

        azure_cse = "azure_cse"
        none = "none"

    class DSLoadFromFileCopyOptionsOnError(Enum):
        """Enum for the DSLoadFromFileCopyOptionsOnError property."""

        abort_statement = "abort_statement"
        cont = "continue"
        skip_file = "skip_file"

    class DSLoadFromFileFileFormat(Enum):
        """Enum for the DSLoadFromFileFileFormat property."""

        avro = "avro"
        csv = "csv"
        orc = "orc"
        parquet = "parquet"

    class DSLoadFromFileFileFormatCompression(Enum):
        """Enum for the DSLoadFromFileFileFormatCompression property."""

        auto = "auto"
        brotli = "brotli"
        bz2 = "bz2"
        deflate = "deflate"
        gzip = "gzip"
        none = "none"
        raw_deflate = "raw_deflate"
        zstd = "zstd"

    class DSLoadFromFileS3Encryption(Enum):
        """Enum for the DSLoadFromFileS3Encryption property."""

        aws_sse_s3 = "aws_sse_s3"
        none = "none"

    class DSLoadFromFileStagingAreaFormatQuotes(Enum):
        """Enum for the DSLoadFromFileStagingAreaFormatQuotes property."""

        double = "double"
        none = "none"
        single = "single"

    class DSLoadFromFileStagingAreaType(Enum):
        """Enum for the DSLoadFromFileStagingAreaType property."""

        external_azure = "external_azure"
        external_gcs = "external_gcs"
        external_s3 = "external_s3"
        internal_location = "internal_location"

    class DSTableAction(Enum):
        """Enum for the DSTableAction property."""

        _append = "_append"
        _create = "_create"
        _replace = "_replace"
        _truncate = "_truncate"

    class DSWriteMode(Enum):
        """Enum for the DSWriteMode property."""

        custom = "custom"
        delete = "delete"
        delete_insert = "delete_insert"
        insert = "insert"
        insert_overwrite = "insert_overwrite"
        insert_update = "insert_update"
        load_from_file = "load_from_file"
        update = "update"

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class MYSQL_COMPOSE:
    """Enums for properties in the MYSQL_COMPOSE stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        call = "call"
        call_statement = "call_statement"
        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        none = "none"
        random = "random"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class InputMethod(Enum):
        """Enum for the InputMethod property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class CredentialsInputMethodSsl(Enum):
        """Enum for the CredentialsInputMethodSsl property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        call = "call"
        call_statement = "call_statement"
        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class DB2FORDATASTAGE:
    """Enums for properties in the DB2FORDATASTAGE stage."""

    class LockWaitMode(Enum):
        """Enum for the LockWaitMode property."""

        return_an_sqlcode_and_sqlstate = "return_an_sqlcode_and_sqlstate"
        use_the_lock_timeout_database_configuration_parameter = "use_the_lock_timeout_database_configuration_parameter"
        user_specified = "user_specified"
        wait_indefinitely = "wait_indefinitely"

    class LookupType(Enum):
        """Enum for the LookupType property."""

        empty = ""
        pxbridge = "pxbridge"

    class Reoptimization(Enum):
        """Enum for the Reoptimization property."""

        always = "always"
        none = "none"
        once = "once"

    class SessionAutocommitMode(Enum):
        """Enum for the SessionAutocommitMode property."""

        off = "off"
        on = "on"

    class SessionIsolationLevel(Enum):
        """Enum for the SessionIsolationLevel property."""

        cursor_stability = "cursor_stability"
        read_stability = "read_stability"
        read_uncommitted = "read_uncommitted"
        repeatable_read = "repeatable_read"

    class SqlEnablePartitioningPartitioningMethod(Enum):
        """Enum for the SqlEnablePartitioningPartitioningMethod property."""

        db2_connector = "db2_connector"
        minimum_and_maximum_range = "minimum_and_maximum_range"
        modulus = "modulus"

    class TransactionEndOfWave(Enum):
        """Enum for the TransactionEndOfWave property."""

        after = "after"
        before = "before"
        none = "none"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        db2part = "db2part"
        db2connector = "db2connector"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class RecordOrdering(Enum):
        """Enum for the RecordOrdering property."""

        zero = 0
        one = 1
        two = 2

    class InputMethod(Enum):
        """Enum for the InputMethod property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class CredentialsInputMethodSsl(Enum):
        """Enum for the CredentialsInputMethodSsl property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class LoadControlAllowAccessMode(Enum):
        """Enum for the LoadControlAllowAccessMode property."""

        no_access = "no_access"
        read = "read"

    class LoadControlCheckPendingCascade(Enum):
        """Enum for the LoadControlCheckPendingCascade property."""

        deferred = "deferred"
        immediate = "immediate"

    class LoadControlCopyLoadedData(Enum):
        """Enum for the LoadControlCopyLoadedData property."""

        no_copy = "no_copy"
        use_tivoli_to_make_a_copy = "use_tivoli_to_make_a_copy"
        use_device_or_directory = "use_device_or_directory"
        use_shared_library = "use_shared_library"

    class LoadControlFileType(Enum):
        """Enum for the LoadControlFileType property."""

        asc = "asc"
        delete = "del"

    class LoadControlIndexingMode(Enum):
        """Enum for the LoadControlIndexingMode property."""

        automatic_selection = "automatic_selection"
        do_not_update_table_indexes = "do_not_update_table_indexes"
        extend_existing_indexes = "extend_existing_indexes"
        rebuild_table_indexes = "rebuild_table_indexes"

    class LoadControlLoadMethod(Enum):
        """Enum for the LoadControlLoadMethod property."""

        named_pipes = "named_pipes"
        sequential_files = "sequential_files"

    class LoadControlLoadMode(Enum):
        """Enum for the LoadControlLoadMode property."""

        insert = "insert"
        replace = "replace"
        restart = "restart"
        terminate = "terminate"

    class LoadControlPartitionedDbConfigIsolatePartErrors(Enum):
        """Enum for the LoadControlPartitionedDbConfigIsolatePartErrors property."""

        load_errors_only = "load_errors_only"
        no_isolation = "no_isolation"
        setup_and_load_errors = "setup_and_load_errors"
        setup_errors_only = "setup_errors_only"

    class LoadControlRestartPhase(Enum):
        """Enum for the LoadControlRestartPhase property."""

        build = "build"
        delete = "delete"
        load = "load"

    class LoadToZosDataFileAttributesDiscardDataSetFileDispositionAbnormalTermination(Enum):
        """Enum for the LoadToZosDataFileAttributesDiscardDataSetFileDispositionAbnormalTermination property."""

        catalog = "catalog"
        delete = "delete"
        keep = "keep"
        uncatalog = "uncatalog"

    class LoadToZosDataFileAttributesDiscardDataSetFileDispositionNormalTermination(Enum):
        """Enum for the LoadToZosDataFileAttributesDiscardDataSetFileDispositionNormalTermination property."""

        catalog = "catalog"
        delete = "delete"
        keep = "keep"
        uncatalog = "uncatalog"

    class LoadToZosDataFileAttributesDiscardDataSetFileDispositionStatus(Enum):
        """Enum for the LoadToZosDataFileAttributesDiscardDataSetFileDispositionStatus property."""

        append = "append"
        new = "new"
        old = "old"
        replace = "replace"
        share = "share"

    class LoadToZosDataFileAttributesDiscardDataSetSpaceType(Enum):
        """Enum for the LoadToZosDataFileAttributesDiscardDataSetSpaceType property."""

        cylinders = "cylinders"
        tracks = "tracks"

    class LoadToZosDataFileAttributesErrorDataSetFileDispositionAbnormalTermination(Enum):
        """Enum for the LoadToZosDataFileAttributesErrorDataSetFileDispositionAbnormalTermination property."""

        catalog = "catalog"
        delete = "delete"
        keep = "keep"
        uncatalog = "uncatalog"

    class LoadToZosDataFileAttributesErrorDataSetFileDispositionNormalTermination(Enum):
        """Enum for the LoadToZosDataFileAttributesErrorDataSetFileDispositionNormalTermination property."""

        catalog = "catalog"
        delete = "delete"
        keep = "keep"
        uncatalog = "uncatalog"

    class LoadToZosDataFileAttributesErrorDataSetFileDispositionStatus(Enum):
        """Enum for the LoadToZosDataFileAttributesErrorDataSetFileDispositionStatus property."""

        append = "append"
        new = "new"
        old = "old"
        replace = "replace"
        share = "share"

    class LoadToZosDataFileAttributesErrorDataSetSpaceType(Enum):
        """Enum for the LoadToZosDataFileAttributesErrorDataSetSpaceType property."""

        cylinders = "cylinders"
        tracks = "tracks"

    class LoadToZosDataFileAttributesInputDataFilesFileDispositionAbnormalTermination(Enum):
        """Enum for the LoadToZosDataFileAttributesInputDataFilesFileDispositionAbnormalTermination property."""

        catalog = "catalog"
        delete = "delete"
        keep = "keep"
        uncatalog = "uncatalog"

    class LoadToZosDataFileAttributesInputDataFilesFileDispositionNormalTermination(Enum):
        """Enum for the LoadToZosDataFileAttributesInputDataFilesFileDispositionNormalTermination property."""

        catalog = "catalog"
        delete = "delete"
        keep = "keep"
        uncatalog = "uncatalog"

    class LoadToZosDataFileAttributesInputDataFilesFileDispositionStatus(Enum):
        """Enum for the LoadToZosDataFileAttributesInputDataFilesFileDispositionStatus property."""

        new = "new"
        old = "old"
        replace = "replace"

    class LoadToZosDataFileAttributesInputDataFilesSpaceType(Enum):
        """Enum for the LoadToZosDataFileAttributesInputDataFilesSpaceType property."""

        cylinders = "cylinders"
        tracks = "tracks"

    class LoadToZosDataFileAttributesMapDataSetFileDispositionAbnormalTermination(Enum):
        """Enum for the LoadToZosDataFileAttributesMapDataSetFileDispositionAbnormalTermination property."""

        catalog = "catalog"
        delete = "delete"
        keep = "keep"
        uncatalog = "uncatalog"

    class LoadToZosDataFileAttributesMapDataSetFileDispositionNormalTermination(Enum):
        """Enum for the LoadToZosDataFileAttributesMapDataSetFileDispositionNormalTermination property."""

        catalog = "catalog"
        delete = "delete"
        keep = "keep"
        uncatalog = "uncatalog"

    class LoadToZosDataFileAttributesMapDataSetFileDispositionStatus(Enum):
        """Enum for the LoadToZosDataFileAttributesMapDataSetFileDispositionStatus property."""

        append = "append"
        new = "new"
        old = "old"
        replace = "replace"
        share = "share"

    class LoadToZosDataFileAttributesMapDataSetSpaceType(Enum):
        """Enum for the LoadToZosDataFileAttributesMapDataSetSpaceType property."""

        cylinders = "cylinders"
        tracks = "tracks"

    class LoadToZosDataFileAttributesWork1DataSetFileDispositionAbnormalTermination(Enum):
        """Enum for the LoadToZosDataFileAttributesWork1DataSetFileDispositionAbnormalTermination property."""

        catalog = "catalog"
        delete = "delete"
        keep = "keep"
        uncatalog = "uncatalog"

    class LoadToZosDataFileAttributesWork1DataSetFileDispositionNormalTermination(Enum):
        """Enum for the LoadToZosDataFileAttributesWork1DataSetFileDispositionNormalTermination property."""

        catalog = "catalog"
        delete = "delete"
        keep = "keep"
        uncatalog = "uncatalog"

    class LoadToZosDataFileAttributesWork1DataSetFileDispositionStatus(Enum):
        """Enum for the LoadToZosDataFileAttributesWork1DataSetFileDispositionStatus property."""

        append = "append"
        new = "new"
        old = "old"
        replace = "replace"
        share = "share"

    class LoadToZosDataFileAttributesWork1DataSetSpaceType(Enum):
        """Enum for the LoadToZosDataFileAttributesWork1DataSetSpaceType property."""

        cylinders = "cylinders"
        tracks = "tracks"

    class LoadToZosDataFileAttributesWork2DataSetFileDispositionAbnormalTermination(Enum):
        """Enum for the LoadToZosDataFileAttributesWork2DataSetFileDispositionAbnormalTermination property."""

        catalog = "catalog"
        delete = "delete"
        keep = "keep"
        uncatalog = "uncatalog"

    class LoadToZosDataFileAttributesWork2DataSetFileDispositionNormalTermination(Enum):
        """Enum for the LoadToZosDataFileAttributesWork2DataSetFileDispositionNormalTermination property."""

        catalog = "catalog"
        delete = "delete"
        keep = "keep"
        uncatalog = "uncatalog"

    class LoadToZosDataFileAttributesWork2DataSetFileDispositionStatus(Enum):
        """Enum for the LoadToZosDataFileAttributesWork2DataSetFileDispositionStatus property."""

        append = "append"
        new = "new"
        old = "old"
        replace = "replace"
        share = "share"

    class LoadToZosDataFileAttributesWork2DataSetSpaceType(Enum):
        """Enum for the LoadToZosDataFileAttributesWork2DataSetSpaceType property."""

        cylinders = "cylinders"
        tracks = "tracks"

    class LoadToZosEncoding(Enum):
        """Enum for the LoadToZosEncoding property."""

        ascii = "ascii"
        ccsid = "ccsid"
        ebcdic = "ebcdic"
        unicode = "unicode"

    class LoadToZosImageCopyFunction(Enum):
        """Enum for the LoadToZosImageCopyFunction property."""

        concurrent = "concurrent"
        full = "full"
        incremental = "incremental"
        no = "no"

    class LoadToZosImageCopyFunctionImageCopyBackupFileFileDispositionAbnormalTermination(Enum):
        """Enum for the LoadToZosImageCopyFunctionImageCopyBackupFileFileDispositionAbnormalTermination property."""

        catalog = "catalog"
        delete = "delete"
        keep = "keep"
        uncatalog = "uncatalog"

    class LoadToZosImageCopyFunctionImageCopyBackupFileFileDispositionNormalTermination(Enum):
        """Enum for the LoadToZosImageCopyFunctionImageCopyBackupFileFileDispositionNormalTermination property."""

        catalog = "catalog"
        delete = "delete"
        keep = "keep"
        uncatalog = "uncatalog"

    class LoadToZosImageCopyFunctionImageCopyBackupFileFileDispositionStatus(Enum):
        """Enum for the LoadToZosImageCopyFunctionImageCopyBackupFileFileDispositionStatus property."""

        append = "append"
        new = "new"
        old = "old"
        replace = "replace"
        share = "share"

    class LoadToZosImageCopyFunctionImageCopyBackupFileSpaceType(Enum):
        """Enum for the LoadToZosImageCopyFunctionImageCopyBackupFileSpaceType property."""

        cylinders = "cylinders"
        tracks = "tracks"

    class LoadToZosImageCopyFunctionImageCopyFileFileDispositionAbnormalTermination(Enum):
        """Enum for the LoadToZosImageCopyFunctionImageCopyFileFileDispositionAbnormalTermination property."""

        catalog = "catalog"
        delete = "delete"
        keep = "keep"
        uncatalog = "uncatalog"

    class LoadToZosImageCopyFunctionImageCopyFileFileDispositionNormalTermination(Enum):
        """Enum for the LoadToZosImageCopyFunctionImageCopyFileFileDispositionNormalTermination property."""

        catalog = "catalog"
        delete = "delete"
        keep = "keep"
        uncatalog = "uncatalog"

    class LoadToZosImageCopyFunctionImageCopyFileFileDispositionStatus(Enum):
        """Enum for the LoadToZosImageCopyFunctionImageCopyFileFileDispositionStatus property."""

        append = "append"
        new = "new"
        old = "old"
        replace = "replace"
        share = "share"

    class LoadToZosImageCopyFunctionImageCopyFileSpaceType(Enum):
        """Enum for the LoadToZosImageCopyFunctionImageCopyFileSpaceType property."""

        cylinders = "cylinders"
        tracks = "tracks"

    class LoadToZosImageCopyFunctionRecoveryBackupFileDispositionAbnormalTermination(Enum):
        """Enum for the LoadToZosImageCopyFunctionRecoveryBackupFileDispositionAbnormalTermination property."""

        catalog = "catalog"
        delete = "delete"
        keep = "keep"
        uncatalog = "uncatalog"

    class LoadToZosImageCopyFunctionRecoveryBackupFileDispositionNormalTermination(Enum):
        """Enum for the LoadToZosImageCopyFunctionRecoveryBackupFileDispositionNormalTermination property."""

        catalog = "catalog"
        delete = "delete"
        keep = "keep"
        uncatalog = "uncatalog"

    class LoadToZosImageCopyFunctionRecoveryBackupFileDispositionStatus(Enum):
        """Enum for the LoadToZosImageCopyFunctionRecoveryBackupFileDispositionStatus property."""

        append = "append"
        new = "new"
        old = "old"
        replace = "replace"
        share = "share"

    class LoadToZosImageCopyFunctionRecoveryBackupSpaceType(Enum):
        """Enum for the LoadToZosImageCopyFunctionRecoveryBackupSpaceType property."""

        cylinders = "cylinders"
        tracks = "tracks"

    class LoadToZosImageCopyFunctionRecoveryFileFileDispositionAbnormalTermination(Enum):
        """Enum for the LoadToZosImageCopyFunctionRecoveryFileFileDispositionAbnormalTermination property."""

        catalog = "catalog"
        delete = "delete"
        keep = "keep"
        uncatalog = "uncatalog"

    class LoadToZosImageCopyFunctionRecoveryFileFileDispositionNormalTermination(Enum):
        """Enum for the LoadToZosImageCopyFunctionRecoveryFileFileDispositionNormalTermination property."""

        catalog = "catalog"
        delete = "delete"
        keep = "keep"
        uncatalog = "uncatalog"

    class LoadToZosImageCopyFunctionRecoveryFileFileDispositionStatus(Enum):
        """Enum for the LoadToZosImageCopyFunctionRecoveryFileFileDispositionStatus property."""

        append = "append"
        new = "new"
        old = "old"
        replace = "replace"
        share = "share"

    class LoadToZosImageCopyFunctionRecoveryFileSpaceType(Enum):
        """Enum for the LoadToZosImageCopyFunctionRecoveryFileSpaceType property."""

        cylinders = "cylinders"
        tracks = "tracks"

    class LoadToZosImageCopyFunctionScope(Enum):
        """Enum for the LoadToZosImageCopyFunctionScope property."""

        full = "full"
        single_partition = "single_partition"

    class LoadToZosLoadMethod(Enum):
        """Enum for the LoadToZosLoadMethod property."""

        batch_pipes = "batch_pipes"
        mvs_datasets = "mvs_datasets"
        uss_pipes = "uss_pipes"

    class LoadToZosShrLevel(Enum):
        """Enum for the LoadToZosShrLevel property."""

        change = "change"
        none = "none"
        reference = "reference"

    class LoadToZosStatistics(Enum):
        """Enum for the LoadToZosStatistics property."""

        all = "all"
        index = "index"
        none = "none"
        table = "table"

    class LoadToZosTransferTransferType(Enum):
        """Enum for the LoadToZosTransferTransferType property."""

        ftp = "ftp"
        lftp = "lftp"
        sftp = "sftp"

    class LoggingLogColumnValuesDelimiter(Enum):
        """Enum for the LoggingLogColumnValuesDelimiter property."""

        comma = "comma"
        newline = "newline"
        space = "space"
        tab = "tab"

    class SessionInsertBuffering(Enum):
        """Enum for the SessionInsertBuffering property."""

        default = "default"
        ignore_duplicates = "ignore_duplicates"
        off = "off"
        on = "on"

    class SessionInsertBufferingAtomicArrays(Enum):
        """Enum for the SessionInsertBufferingAtomicArrays property."""

        auto = "auto"
        no = "no"
        simulated = "simulated"
        yes = "yes"

    class SessionTemporaryWorkTable(Enum):
        """Enum for the SessionTemporaryWorkTable property."""

        automatic = "automatic"
        existing = "existing"

    class SqlUserDefinedSql(Enum):
        """Enum for the SqlUserDefinedSql property."""

        file = "file"
        statements = "statements"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        create = "create"
        replace = "replace"
        truncate = "truncate"

    class TableActionGenerateCreateStatementCreateTableCompress(Enum):
        """Enum for the TableActionGenerateCreateStatementCreateTableCompress property."""

        database_default = "database_default"
        no = "no"
        yes = "yes"

    class TableActionGenerateCreateStatementCreateTableCompressCreateTableCompressLuw(Enum):
        """Enum for the TableActionGenerateCreateStatementCreateTableCompressCreateTableCompressLuw property."""

        adaptive = "adaptive"
        static = "static"

    class TableActionGenerateCreateStatementCreateTableDistributeBy(Enum):
        """Enum for the TableActionGenerateCreateStatementCreateTableDistributeBy property."""

        hash = "hash"
        none = "none"
        random = "random"

    class TableActionGenerateCreateStatementCreateTableOrganizeBy(Enum):
        """Enum for the TableActionGenerateCreateStatementCreateTableOrganizeBy property."""

        column = "column"
        database_default = "database_default"
        row = "row"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        bulk_load = "bulk_load"
        delete = "delete"
        delete_then_insert = "delete_then_insert"
        insert = "insert"
        insert_new_rows_only = "insert_new_rows_only"
        insert_then_update = "insert_then_update"
        update = "update"
        update_then_insert = "update_then_insert"
        user_defined_sql = "user-defined_sql"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class AMAZONRDS_ORACLE:
    """Enums for properties in the AMAZONRDS_ORACLE stage."""

    class NumberType(Enum):
        """Enum for the NumberType property."""

        double = "double"
        varchar = "varchar"

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        block = "block"
        none = "none"
        row = "row"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class DB2ISERIES:
    """Enums for properties in the DB2ISERIES stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        call = "call"
        call_statement = "call_statement"
        general = "general"
        select = "select"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class InputMethod(Enum):
        """Enum for the InputMethod property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class CredentialsInputMethodSsl(Enum):
        """Enum for the CredentialsInputMethodSsl property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        call = "call"
        call_statement = "call_statement"
        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class AZURESYNAPSE:
    """Enums for properties in the AZURESYNAPSE stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        call = "call"
        call_statement = "call_statement"
        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        none = "none"
        random = "random"
        row = "row"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        call = "call"
        call_statement = "call_statement"
        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class MYSQL_AMAZON:
    """Enums for properties in the MYSQL_AMAZON stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        call = "call"
        call_statement = "call_statement"
        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        none = "none"
        random = "random"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class InputMethod(Enum):
        """Enum for the InputMethod property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class CredentialsInputMethodSsl(Enum):
        """Enum for the CredentialsInputMethodSsl property."""

        enter_credentials_manually = "enter_credentials_manually"
        use_vault_secrets = "use_vault_secrets"

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        call = "call"
        call_statement = "call_statement"
        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectConditionPropertiesOption(Enum):
        """Enum for the RejectConditionPropertiesOption property."""

        Row_is_rejected = "Row is rejected"

    class RejectRowsPropertiesSet(Enum):
        """Enum for the RejectRowsPropertiesSet property."""

        ERRORCODE = "ERRORCODE"
        ERRORTEXT = "ERRORTEXT"

    class AbortWhen(Enum):
        """Enum for the AbortWhen property."""

        rows = "rows"
        percent = "percent"

    class RejectFromLink(Enum):
        """Enum for the RejectFromLink property."""

        Link_1 = "Link_1"


class COGNOS_ANALYTICS:
    """Enums for properties in the COGNOS_ANALYTICS stage."""

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        read_single = "read_single"
        read_raw = "read_raw"
        read_raw_multiple_wildcard = "read_raw_multiple_wildcard"
        read_multiple_regex = "read_multiple_regex"
        read_multiple_wildcard = "read_multiple_wildcard"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1


class VERTICA:
    """Enums for properties in the VERTICA stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        block = "block"
        none = "none"
        row = "row"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class ELASTICSEARCH:
    """Enums for properties in the ELASTICSEARCH stage."""

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        read_single = "read_single"
        read_raw = "read_raw"
        read_raw_multiple_wildcard = "read_raw_multiple_wildcard"
        read_multiple_regex = "read_multiple_regex"
        read_multiple_wildcard = "read_multiple_wildcard"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class FileAction(Enum):
        """Enum for the FileAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        delete = "delete"
        write = "write"
        write_raw = "write_raw"


class AMAZON_POSTGRESQL:
    """Enums for properties in the AMAZON_POSTGRESQL stage."""

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        call = "call"
        call_statement = "call_statement"
        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        block = "block"
        none = "none"
        random = "random"
        row = "row"

    class LookupType(Enum):
        """Enum for the LookupType property."""

        empty = "empty"
        pxbridge = "pxbridge"

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        call = "call"
        call_statement = "call_statement"
        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class SAPHANA:
    """Enums for properties in the SAPHANA stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class SAPODATA:
    """Enums for properties in the SAPODATA stage."""

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        update = "update"


class SINGLESTORE:
    """Enums for properties in the SINGLESTORE stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class SamplingType(Enum):
        """Enum for the SamplingType property."""

        none = "none"
        random = "random"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class ExistingTableAction(Enum):
        """Enum for the ExistingTableAction property."""

        append = "append"
        merge = "merge"
        replace = "replace"
        truncate = "truncate"
        update = "update"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class AZURE_BLOB_STORAGE:
    """Enums for properties in the AZURE_BLOB_STORAGE stage."""

    class DSFileFormat(Enum):
        """Enum for the DSFileFormat property."""

        comma_separated_value_csv = "comma-separated_value_csv"
        delimited = "delimited"

    class DSReadMode(Enum):
        """Enum for the DSReadMode property."""

        list_containers_fileshares = "list_containers/fileshares"
        list_files = "list_files"
        read_multiple_files = "read_multiple_files"
        read_single_file = "read_single_file"

    class DelimitedSyntaxQuotes(Enum):
        """Enum for the DelimitedSyntaxQuotes property."""

        double = "double"
        none = "none"
        single = "single"

    class DelimitedSyntaxRecordDef(Enum):
        """Enum for the DelimitedSyntaxRecordDef property."""

        delimited_string = "delimited_string"
        delimited_string_in_a_file = "delimited_string_in_a_file"
        file_header = "file_header"
        none = "none"
        schema_file = "schema_file"

    class LookupType(Enum):
        """Enum for the LookupType property."""

        empty = "empty"
        pxbridge = "pxbridge"

    class RejectMode(Enum):
        """Enum for the RejectMode property."""

        cont = "continue"
        fail = "fail"
        reject = "reject"

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class EscapeCharacter(Enum):
        """Enum for the EscapeCharacter property."""

        question = "<?>"
        backslash = "backslash"
        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class FieldDelimiter(Enum):
        """Enum for the FieldDelimiter property."""

        question = "<?>"
        colon = "colon"
        comma = "comma"
        tab = "tab"

    class FileFormat(Enum):
        """Enum for the FileFormat property."""

        avro = "avro"
        csv = "csv"
        delimited = "delimited"
        excel = "excel"
        json = "json"
        orc = "orc"
        parquet = "parquet"
        sav = "sav"
        xml = "xml"

    class InvalidDataHandling(Enum):
        """Enum for the InvalidDataHandling property."""

        column = "column"
        fail = "fail"
        row = "row"

    class QuoteCharacter(Enum):
        """Enum for the QuoteCharacter property."""

        double_quote = "double_quote"
        none = "none"
        single_quote = "single_quote"

    class ReadMode(Enum):
        """Enum for the ReadMode property."""

        read_single = "read_single"
        read_raw = "read_raw"
        read_raw_multiple_wildcard = "read_raw_multiple_wildcard"
        read_multiple_regex = "read_multiple_regex"
        read_multiple_wildcard = "read_multiple_wildcard"

    class RowDelimiter(Enum):
        """Enum for the RowDelimiter property."""

        question = "<?>"
        new_line = "new_line"
        carriage_return = "carriage_return"
        carriage_return_line_feed = "carriage_return_line_feed"
        line_feed = "line_feed"

    class TableFormat(Enum):
        """Enum for the TableFormat property."""

        deltalake = "deltalake"
        file = "file"
        iceberg = "iceberg"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class DSWriteMode(Enum):
        """Enum for the DSWriteMode property."""

        delete = "delete"
        write = "write"

    class FileExists(Enum):
        """Enum for the FileExists property."""

        do_not_overwrite_file = "do_not_overwrite_file"
        fail = "fail"
        overwrite_file = "overwrite_file"

    class BlobType(Enum):
        """Enum for the BlobType property."""

        append = "append"
        block = "block"
        page = "page"

    class CodecAvro(Enum):
        """Enum for the CodecAvro property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        null = "null"
        snappy = "snappy"

    class CodecCsv(Enum):
        """Enum for the CodecCsv property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecDelimited(Enum):
        """Enum for the CodecDelimited property."""

        gzip = "gzip"
        uncompressed = "uncompressed"

    class CodecOrc(Enum):
        """Enum for the CodecOrc property."""

        lz4 = "lz4"
        lzo = "lzo"
        none = "none"
        snappy = "snappy"
        zlib = "zlib"

    class CodecParquet(Enum):
        """Enum for the CodecParquet property."""

        gzip = "gzip"
        uncompressed = "uncompressed"
        snappy = "snappy"

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class TableDataFileCompressionCodec(Enum):
        """Enum for the TableDataFileCompressionCodec property."""

        bzip2 = "bzip2"
        deflate = "deflate"
        gzip = "gzip"
        lz4 = "lz4"
        lzo = "lzo"
        uncompressed = "uncompressed"
        snappy = "snappy"
        zlib = "zlib"

    class TableDataFileFormat(Enum):
        """Enum for the TableDataFileFormat property."""

        avro = "avro"
        orc = "orc"
        parquet = "parquet"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        delete = "delete"
        write = "write"
        write_raw = "write_raw"


class DATASTAX:
    """Enums for properties in the DATASTAX stage."""

    class DecimalRoundingMode(Enum):
        """Enum for the DecimalRoundingMode property."""

        ceiling = "ceiling"
        down = "down"
        floor = "floor"
        halfdown = "halfdown"
        halfeven = "halfeven"
        halfup = "halfup"
        up = "up"

    class ReadMethod(Enum):
        """Enum for the ReadMethod property."""

        general = "general"
        select = "select"

    class PartitionType(Enum):
        """Enum for the PartitionType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class CombinabilityMode(Enum):
        """Enum for the CombinabilityMode property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class BufferingMode(Enum):
        """Enum for the BufferingMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class Collecting(Enum):
        """Enum for the Collecting property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class ExecutionMode(Enum):
        """Enum for the ExecutionMode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class PreservePartitioning(Enum):
        """Enum for the PreservePartitioning property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class TableAction(Enum):
        """Enum for the TableAction property."""

        append = "append"
        replace = "replace"
        truncate = "truncate"

    class WriteMode(Enum):
        """Enum for the WriteMode property."""

        insert = "insert"
        merge = "merge"
        update = "update"
        update_statement = "update_statement"
        update_statement_table_action = "update_statement_table_action"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        rows = "rows"
        percent = "percent"


class HIERARCHICAL_DATA:
    """Enums for properties in the HIERARCHICAL_DATA stage."""

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_seq = "default_seq"
        par = "par"
        seq = "seq"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class SplitBatchKeyValueOrder(Enum):
        """Enum for the SplitBatchKeyValueOrder property."""

        ascending = "ascending"
        descending = "descending"

    class LogLevel(Enum):
        """Enum for the LogLevel property."""

        debug = "debug"
        error = "error"
        fatal = "fatal"
        info = "info"
        trace = "trace"
        warning = "warning"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class WEB_SERVICE:
    """Enums for properties in the WEB_SERVICE stage."""

    class LogResponse(Enum):
        """Enum for the LogResponse property."""

        zero = 0
        one = 1
        two = 2

    class TruststoreType(Enum):
        """Enum for the TruststoreType property."""

        JKS = "JKS"
        PKCS12 = "PKCS12"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_seq = "default_seq"
        seq = "seq"
        par = "par"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_set = -2
        default_clear = -1
        clear = 0
        set = 1

    class ErrorHandling(Enum):
        """Enum for the ErrorHandling property."""

        trace = 1
        info = 3
        warning = 4
        reject = 5
        fatal = 6

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class XML_OUTPUT:
    """Enums for properties in the XML_OUTPUT stage."""

    class XmlValidationLevel(Enum):
        """Enum for the XmlValidationLevel property."""

        default = "0"
        strict = "1"

    class XmlFatalMapping(Enum):
        """Enum for the XmlFatalMapping property."""

        DS_REJECT = "DS_REJECT"
        DS_FATAL = "DS_FATAL"
        DS_WARNING = "DS_WARNING"
        DS_INFO = "DS_INFO"
        DS_TRACE = "DS_TRACE"

    class XmlErrorMapping(Enum):
        """Enum for the XmlErrorMapping property."""

        DS_REJECT = "DS_REJECT"
        DS_FATAL = "DS_FATAL"
        DS_WARNING = "DS_WARNING"
        DS_INFO = "DS_INFO"
        DS_TRACE = "DS_TRACE"

    class XmlWarningMapping(Enum):
        """Enum for the XmlWarningMapping property."""

        DS_REJECT = "DS_REJECT"
        DS_FATAL = "DS_FATAL"
        DS_WARNING = "DS_WARNING"
        DS_INFO = "DS_INFO"
        DS_TRACE = "DS_TRACE"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_seq = "default_seq"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class JAVA_INTEGRATION:
    """Enums for properties in the JAVA_INTEGRATION stage."""

    class LookupType(Enum):
        """Enum for the LookupType property."""

        empty = ""
        pxbridge = "pxbridge"

    class RejectUses(Enum):
        """Enum for the RejectUses property."""

        Percent = "Percent"
        Rows = "Rows"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"

    class RejectConditionPropertiesOption(Enum):
        """Enum for the RejectConditionPropertiesOption property."""

        Row_rejected = "Row rejected"

    class RejectRowsPropertiesSet(Enum):
        """Enum for the RejectRowsPropertiesSet property."""

        ERRORCODE = "ERRORCODE"
        ERRORTEXT = "ERRORTEXT"


class XML_INPUT:
    """Enums for properties in the XML_INPUT stage."""

    class XmlSourceColumn(Enum):
        """Enum for the XmlSourceColumn property."""

        false = ""

    class XmlText(Enum):
        """Enum for the XmlText property."""

        text = "text"
        URL = "URL"

    class RejectMessageColumn(Enum):
        """Enum for the RejectMessageColumn property."""

        custom = " "

    class XsltSource(Enum):
        """Enum for the XsltSource property."""

        column = "column"
        property = "property"

    class XsltText(Enum):
        """Enum for the XsltText property."""

        text = "text"
        URL = "URL"

    class XmlValidationLevel(Enum):
        """Enum for the XmlValidationLevel property."""

        default = "0"
        strict = "1"

    class XsltFatalMapping(Enum):
        """Enum for the XsltFatalMapping property."""

        DS_REJECT = "DS_REJECT"
        DS_FATAL = "DS_FATAL"
        DS_WARNING = "DS_WARNING"
        DS_INFO = "DS_INFO"
        DS_TRACE = "DS_TRACE"

    class XsltErrorMapping(Enum):
        """Enum for the XsltErrorMapping property."""

        DS_REJECT = "DS_REJECT"
        DS_FATAL = "DS_FATAL"
        DS_WARNING = "DS_WARNING"
        DS_INFO = "DS_INFO"
        DS_TRACE = "DS_TRACE"

    class XsltWarningMapping(Enum):
        """Enum for the XsltWarningMapping property."""

        DS_REJECT = "DS_REJECT"
        DS_FATAL = "DS_FATAL"
        DS_WARNING = "DS_WARNING"
        DS_INFO = "DS_INFO"
        DS_TRACE = "DS_TRACE"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_seq = "default_seq"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1

    class PartType(Enum):
        """Enum for the PartType property."""

        auto = "auto"
        entire = "entire"
        random = "random"
        roundrobin = "roundrobin"
        same = "same"
        modulus = "modulus"
        hash = "hash"
        range = "range"

    class BufMode(Enum):
        """Enum for the BufMode property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class BufModeRonly(Enum):
        """Enum for the BufModeRonly property."""

        default = "default"
        autobuffer = "autobuffer"
        buffer = "buffer"
        nobuffer = "nobuffer"

    class KeyColSelect(Enum):
        """Enum for the KeyColSelect property."""

        default = "default"

    class CollType(Enum):
        """Enum for the CollType property."""

        auto = "auto"
        ordered = "ordered"
        roundrobin_coll = "roundrobin_coll"
        sortmerge = "sortmerge"


class REST:
    """Enums for properties in the REST stage."""

    class RejectMessageColumn(Enum):
        """Enum for the RejectMessageColumn property."""

        custom = " "

    class LogLevel(Enum):
        """Enum for the LogLevel property."""

        debug = "debug"
        error = "error"
        fatal = "fatal"
        info = "info"
        warning = "warning"

    class Execmode(Enum):
        """Enum for the Execmode property."""

        default_seq = "default_seq"
        default_par = "default_par"
        par = "par"
        seq = "seq"

    class Combinability(Enum):
        """Enum for the Combinability property."""

        auto = "auto"
        combine = "combine"
        nocombine = "nocombine"

    class Preserve(Enum):
        """Enum for the Preserve property."""

        default_propagate = -3
        clear = 0
        propagate = 2
        set = 1


class SALESFORCEAPI_CONNECTION:
    """Enums for properties in the SALESFORCEAPI connection."""

    class AuthenticationType(Enum):
        """Enum for the AuthenticationType property."""

        oauth_jwt = "oauth_jwt"
        oauth_username_and_password = "oauth_username_and_password"
        username_and_password = "username_and_password"


class SAPDELTAEXTRACT_CONNECTION:
    """Enums for properties in the SAPDELTAEXTRACT connection."""

    class ConnectionType(Enum):
        """Enum for the ConnectionType property."""

        application_server = "application_server"
        load_balancing = "load_balancing"
        snc_application_server = "snc_application_server"
        snc_load_balancing = "snc_load_balancing"

    class SncQop(Enum):
        """Enum for the SncQop property."""

        auth_only = "1"
        auth_integrity = "2"
        auth_integrity_privacy = "3"
        global_default = "8"
        max_protection = "9"


class FTP_CONNECTION:
    """Enums for properties in the FTP connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        username_password = "username_password"
        username_password_key = "username_password_key"
        username_key = "username_key"

    class ConnectionMode(Enum):
        """Enum for the ConnectionMode property."""

        anonymous = "anonymous"
        basic = "basic"
        mvssftp = "mvssftp"
        sftp = "sftp"
        ftps = "ftps"


class MONGODB_IBMCLOUD_CONNECTION:
    """Enums for properties in the MONGODB_IBMCLOUD connection."""

    class SpecialCharBehavior(Enum):
        """Enum for the SpecialCharBehavior property."""

        include = "include"
        replace = "replace"
        strip = "strip"


class SAPBULKEXTRACT_CONNECTION:
    """Enums for properties in the SAPBULKEXTRACT connection."""

    class ConnectionType(Enum):
        """Enum for the ConnectionType property."""

        application_server = "application_server"
        load_balancing = "load_balancing"
        snc_application_server = "snc_application_server"
        snc_load_balancing = "snc_load_balancing"

    class SncQop(Enum):
        """Enum for the SncQop property."""

        auth_only = "1"
        auth_integrity = "2"
        auth_integrity_privacy = "3"
        global_default = "8"
        max_protection = "9"


class AZURE_FILE_STORAGE_CONNECTION:
    """Enums for properties in the AZURE_FILE_STORAGE connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        connection_string = "connection_string"
        entra_id = "entra_id"
        entra_id_user = "entra_id_user"


class ORACLE_DATASTAGE_CONNECTION:
    """Enums for properties in the ORACLE_DATASTAGE connection."""

    class ConnectionType(Enum):
        """Enum for the ConnectionType property."""

        ldap = "ldap"
        seps = "seps"
        tcp = "tcp"
        tcps = "tcps"


class GENERICS3_CONNECTION:
    """Enums for properties in the GENERICS3 connection."""

    class ListObjectsApiVersion(Enum):
        """Enum for the ListObjectsApiVersion property."""

        v1 = "v1"
        v2 = "v2"


class PLANNING_ANALYTICS_CONNECTION:
    """Enums for properties in the PLANNING_ANALYTICS connection."""

    class AuthType(Enum):
        """Enum for the AuthType property."""

        bearer = "bearer"
        cam_credentials = "cam_credentials"
        basic = "basic"


class DREMIO_CONNECTION:
    """Enums for properties in the DREMIO connection."""

    class AuthType(Enum):
        """Enum for the AuthType property."""

        token = "token"
        user_pass = "user_pass"


class TABLEAU_CONNECTION:
    """Enums for properties in the TABLEAU connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        access_token = "access_token"
        username_and_password = "username_and_password"


class TERADATA_CONNECTION:
    """Enums for properties in the TERADATA connection."""

    class AuthenticationMethod(Enum):
        """Enum for the AuthenticationMethod property."""

        ldap = "ldap"
        td2 = "td2"


class CLOUD_OBJECT_STORAGE_CONNECTION:
    """Enums for properties in the CLOUD_OBJECT_STORAGE connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        accesskey_secretkey = "accesskey_secretkey"
        instanceid_apikey = "instanceid_apikey"
        instanceid_apikey_accesskey_secretkey = "instanceid_apikey_accesskey_secretkey"
        credentials = "credentials"


class APACHE_KAFKA_CONNECTION:
    """Enums for properties in the APACHE_KAFKA connection."""

    class SaslOauthbearer(Enum):
        """Enum for the SaslOauthbearer property."""

        SASL_OAUTH2 = "SASL_OAUTH2"

    class SchemaRegistryAuthentication(Enum):
        """Enum for the SchemaRegistryAuthentication property."""

        none = "none"
        reuse_sasl_credentials = "reuse_sasl_credentials"
        user_credentials = "user_credentials"

    class SchemaRegistrySecure(Enum):
        """Enum for the SchemaRegistrySecure property."""

        kerberos = "kerberos"
        none = "none"
        ssl = "ssl"
        reuse_ssl = "reuse_ssl"

    class SchemaRegistryType(Enum):
        """Enum for the SchemaRegistryType property."""

        confluent = "confluent"
        eventstreamsconfluent = "eventstreamsconfluent"

    class SecureConnection(Enum):
        """Enum for the SecureConnection property."""

        kerberos = "kerberos"
        none = "None"
        SASL_OAUTHBEARER = "SASL_OAUTHBEARER"
        SASL_PLAIN = "SASL_PLAIN"
        SASL_SSL = "SASL_SSL"
        SCRAM_SHA_256 = "SCRAM-SHA-256"
        SCRAM_SHA_512 = "SCRAM-SHA-512"
        SSL = "SSL"


class WATSONX_DATA_CONNECTION:
    """Enums for properties in the WATSONX_DATA connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        username_apikey = "username_apikey"
        username_password = "username_password"

    class DeploymentType(Enum):
        """Enum for the DeploymentType property."""

        software_dev = "software_dev"
        saas = "saas"
        software_ent = "software_ent"


class TERADATA_DATASTAGE_CONNECTION:
    """Enums for properties in the TERADATA_DATASTAGE connection."""

    class LogOnMech(Enum):
        """Enum for the LogOnMech property."""

        default = "default"
        ldap = "ldap"
        td2 = "td2"

    class SslMode(Enum):
        """Enum for the SslMode property."""

        allow = "allow"
        disable = "disable"
        prefer = "prefer"
        require = "require"
        verify_ca = "verify_ca"
        verify_full = "verify_full"

    class SslModeSslProtocol(Enum):
        """Enum for the SslModeSslProtocol property."""

        TLS1_2 = "TLS1_2"

    class TransactionMode(Enum):
        """Enum for the TransactionMode property."""

        ansi = "ansi"
        teradata = "teradata"


class APACHE_HBASE_CONNECTION:
    """Enums for properties in the APACHE_HBASE connection."""

    class FilePathMode(Enum):
        """Enum for the FilePathMode property."""

        content = "content"
        path = "path"


class ORACLE_CONNECTION:
    """Enums for properties in the ORACLE connection."""

    class ConnectionMode(Enum):
        """Enum for the ConnectionMode property."""

        sid = "sid"
        service_name = "service_name"

    class FailoverMode(Enum):
        """Enum for the FailoverMode property."""

        connect = "connect"
        extended = "extended"
        select = "select"

    class MetadataDiscovery(Enum):
        """Enum for the MetadataDiscovery property."""

        no_remarks = "no_remarks"
        no_remarks_or_synonyms = "no_remarks_or_synonyms"
        no_synonyms = "no_synonyms"
        remarks_and_synonyms = "remarks_and_synonyms"

    class NumberType(Enum):
        """Enum for the NumberType property."""

        double = "double"
        varchar = "varchar"


class AMAZONS3_CONNECTION:
    """Enums for properties in the AMAZONS3 connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        basic_credentials = "basic_credentials"
        temporary_credentials = "temporary_credentials"
        trusted_role_credentials = "trusted_role_credentials"


class AZURE_COSMOS_CONNECTION:
    """Enums for properties in the AZURE_COSMOS connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        entra_id = "entra_id"
        entra_id_user = "entra_id_user"
        master_key = "master_key"


class AZURE_DATABRICKS_CONNECTION:
    """Enums for properties in the AZURE_DATABRICKS connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        entra_id = "entra_id"
        oauth_m2m = "oauth_m2m"
        userpass = "userpass"


class CASSANDRA_DATASTAGE_CONNECTION:
    """Enums for properties in the CASSANDRA_DATASTAGE connection."""

    class AuthenticatorType(Enum):
        """Enum for the AuthenticatorType property."""

        allow_all_authenticator = "allow_all_authenticator"
        password_authentication = "password_authentication"

    class Compression(Enum):
        """Enum for the Compression property."""

        lz4 = "lz4"
        no_compression = "no_compression"
        snappy = "snappy"

    class ProtocolVersion(Enum):
        """Enum for the ProtocolVersion property."""

        dse_v1 = "dse_v1"
        dse_v2 = "dse_v2"
        newest_supported = "newest_supported"
        newest_beta = "newest_beta"
        v1 = "v1"
        v2 = "v2"
        v3 = "v3"
        v4 = "v4"
        v5 = "v5"
        v9 = "v9"


class HDFS_APACHE_CONNECTION:
    """Enums for properties in the HDFS_APACHE connection."""

    class AuthenticationMethod(Enum):
        """Enum for the AuthenticationMethod property."""

        kerberos = "kerberos"
        password = "password"

    class FilesystemType(Enum):
        """Enum for the FilesystemType property."""

        httpfs = "httpfs"
        webhdfs = "webhdfs"


class AMAZON_REDSHIFT_CONNECTION:
    """Enums for properties in the AMAZON_REDSHIFT connection."""

    class TimeType(Enum):
        """Enum for the TimeType property."""

        time = "time"
        timestamp = "timestamp"
        varchar = "varchar"


class IMPALA_CONNECTION:
    """Enums for properties in the IMPALA connection."""

    class AuthenticationMethod(Enum):
        """Enum for the AuthenticationMethod property."""

        kerberos = "kerberos"
        ldap = "ldap"
        password = "password"


class BIGQUERY_CONNECTION:
    """Enums for properties in the BIGQUERY connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        credentials = "credentials"
        credentials_oauth2 = "credentials_oauth2"
        workload_identity_federation_token = "workload_identity_federation_token"
        workload_identity_federation_token_url = "workload_identity_federation_token_url"

    class JsonFormat(Enum):
        """Enum for the JsonFormat property."""

        pretty = "pretty"
        raw = "raw"

    class MetadataDiscovery(Enum):
        """Enum for the MetadataDiscovery property."""

        no_remarks = "no_remarks"
        remarks = "remarks"

    class ProxyProtocol(Enum):
        """Enum for the ProxyProtocol property."""

        http = "http"
        https = "https"

    class TokenFormat(Enum):
        """Enum for the TokenFormat property."""

        json = "json"
        text = "text"

    class TokenType(Enum):
        """Enum for the TokenType property."""

        aws4_request = "aws4_request"
        access_token = "access_token"
        id_token = "id_token"
        jwt = "jwt"
        saml2 = "saml2"

    class TokenUrlMethod(Enum):
        """Enum for the TokenUrlMethod property."""

        get = "get"
        post = "post"
        put = "put"


class IBM_MQ_CONNECTION:
    """Enums for properties in the IBM_MQ connection."""

    class ClientChannelDefinitionTransportType(Enum):
        """Enum for the ClientChannelDefinitionTransportType property."""

        tcp = "tcp"
        udp = "udp"


class JDBC_CONNECTION:
    """Enums for properties in the JDBC connection."""

    class RowLimitSupport(Enum):
        """Enum for the RowLimitSupport property."""

        none = "none"
        prefix = "prefix"
        suffix = "suffix"


class SAPIDOC_CONNECTION:
    """Enums for properties in the SAPIDOC connection."""

    class ConnectionType(Enum):
        """Enum for the ConnectionType property."""

        application_server = "application_server"
        load_balancing = "load_balancing"
        snc_application_server = "snc_application_server"
        snc_load_balancing = "snc_load_balancing"

    class SncQop(Enum):
        """Enum for the SncQop property."""

        auth_only = "1"
        auth_integrity = "2"
        auth_integrity_privacy = "3"
        global_default = "8"
        max_protection = "9"


class DB2WAREHOUSE_CONNECTION:
    """Enums for properties in the DB2WAREHOUSE connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        apikey = "apikey"
        username_password = "username_password"


class MONGODB_CONNECTION:
    """Enums for properties in the MONGODB connection."""

    class SpecialCharBehavior(Enum):
        """Enum for the SpecialCharBehavior property."""

        include = "include"
        replace = "replace"
        strip = "strip"


class GOOGLE_CLOUD_STORAGE_CONNECTION:
    """Enums for properties in the GOOGLE_CLOUD_STORAGE connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        credentials = "credentials"
        credentials_oauth2 = "credentials_oauth2"
        workload_identity_federation_token = "workload_identity_federation_token"
        workload_identity_federation_token_url = "workload_identity_federation_token_url"

    class ProxyProtocol(Enum):
        """Enum for the ProxyProtocol property."""

        http = "http"
        https = "https"

    class TokenFormat(Enum):
        """Enum for the TokenFormat property."""

        json = "json"
        text = "text"

    class TokenType(Enum):
        """Enum for the TokenType property."""

        aws4_request = "aws4_request"
        access_token = "access_token"
        id_token = "id_token"
        jwt = "jwt"
        saml2 = "saml2"

    class TokenUrlMethod(Enum):
        """Enum for the TokenUrlMethod property."""

        get = "get"
        post = "post"
        put = "put"


class ODBC_CONNECTION:
    """Enums for properties in the ODBC connection."""

    class AuthenticationMethod(Enum):
        """Enum for the AuthenticationMethod property."""

        oauth2 = "oauth2"
        serviceaccount = "serviceaccount"

    class DsnType(Enum):
        """Enum for the DsnType property."""

        Cassandra = "Cassandra"
        Hive = "Hive"
        Googlebigquery = "Googlebigquery"
        GreenPlum = "GreenPlum"
        DB2 = "DB2"
        DB2zOS = "DB2zOS"
        DB2AS400 = "DB2AS400"
        Informix = "Informix"
        Netezza = "Netezza"
        Impala = "Impala"
        MicrosoftSQLServer = "MicrosoftSQLServer"
        MongoDB = "MongoDB"
        MySQL = "MySQL"
        Oracle = "Oracle"
        PostgreSQL = "PostgreSQL"
        SybaseASE = "SybaseASE"
        SybaseIQ = "SybaseIQ"
        Teradata = "Teradata"
        Text = "Text"
        use_dsn_name = "use_dsn_name"

    class LogOnMech(Enum):
        """Enum for the LogOnMech property."""

        ldap = "ldap"
        td2 = "td2"

    class ServiceAccountKeyInputMethod(Enum):
        """Enum for the ServiceAccountKeyInputMethod property."""

        keycontent = "keycontent"
        keyfile = "keyfile"


class DV_CONNECTION:
    """Enums for properties in the DV connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        apikey = "apikey"
        username_password = "username_password"

    class InstanceEnvironment(Enum):
        """Enum for the InstanceEnvironment property."""

        cloud = "cloud"
        private = "private"


class CASSANDRA_CONNECTION:
    """Enums for properties in the CASSANDRA connection."""

    class ReadConsistency(Enum):
        """Enum for the ReadConsistency property."""

        all = "all"
        local_one = "local_one"
        local_quorum = "local_quorum"
        local_serial = "local_serial"
        one = "one"
        quorum = "quorum"
        serial = "serial"
        three = "three"
        two = "two"

    class WriteConsistency(Enum):
        """Enum for the WriteConsistency property."""

        all = "all"
        any = "any"
        each_quorum = "each_quorum"
        local_one = "local_one"
        local_quorum = "local_quorum"
        local_serial = "local_serial"
        one = "one"
        quorum = "quorum"
        serial = "serial"
        three = "three"
        two = "two"


class AZURE_POSTGRESQL_CONNECTION:
    """Enums for properties in the AZURE_POSTGRESQL connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        entra_id_service = "entra_id_service"
        entra_id_user = "entra_id_user"
        user_credentials = "user_credentials"


class SQLSERVER_CONNECTION:
    """Enums for properties in the SQLSERVER connection."""

    class NtlmVersion(Enum):
        """Enum for the NtlmVersion property."""

        default = "default"
        v2 = "v2"


class AZUREDATALAKE_CONNECTION:
    """Enums for properties in the AZUREDATALAKE connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        client_credentials = "client_credentials"
        username_password = "username_password"

    class ProxyProtocol(Enum):
        """Enum for the ProxyProtocol property."""

        http = "http"
        https = "https"


class GOOGLE_PUB_SUB_CONNECTION:
    """Enums for properties in the GOOGLE_PUB_SUB connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        credentials = "credentials"
        credentials_oauth2 = "credentials_oauth2"
        credentials_file = "credentials_file"
        workload_identity_federation_token = "workload_identity_federation_token"
        workload_identity_federation_token_url = "workload_identity_federation_token_url"

    class TokenFormat(Enum):
        """Enum for the TokenFormat property."""

        json = "json"
        text = "text"

    class TokenType(Enum):
        """Enum for the TokenType property."""

        aws4_request = "aws4_request"
        access_token = "access_token"
        id_token = "id_token"
        jwt = "jwt"
        saml2 = "saml2"

    class TokenUrlMethod(Enum):
        """Enum for the TokenUrlMethod property."""

        get = "get"
        post = "post"
        put = "put"


class DROPBOX_CONNECTION:
    """Enums for properties in the DROPBOX connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        accesstoken = "accesstoken"
        refreshtoken = "refreshtoken"


class AZURESQL_CONNECTION:
    """Enums for properties in the AZURESQL connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        entra_id_service = "entra_id_service"
        entra_id_user = "entra_id_user"
        user_credentials = "user_credentials"


class DB2_CONNECTION:
    """Enums for properties in the DB2 connection."""

    class UsernamePasswordEncryption(Enum):
        """Enum for the UsernamePasswordEncryption property."""

        aes_256_bit = "aes_256_bit"
        des_56_bit = "des_56_bit"
        default = "default"

    class UsernamePasswordSecurity(Enum):
        """Enum for the UsernamePasswordSecurity property."""

        clear_text = "clear_text"
        default = "default"
        encrypted_password = "encrypted_password"
        encrypted_username = "encrypted_username"
        encrypted_username_password = "encrypted_username_password"
        encrypted_username_password_data = "encrypted_username_password_data"
        kerberos_credentials = "kerberos_credentials"


class APACHE_HIVE_CONNECTION:
    """Enums for properties in the APACHE_HIVE connection."""

    class AuthenticationMethod(Enum):
        """Enum for the AuthenticationMethod property."""

        kerberos = "kerberos"
        password = "password"


class SNOWFLAKE_CONNECTION:
    """Enums for properties in the SNOWFLAKE connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        key_pair = "key_pair"
        username_password = "username_password"

    class LineageExtractionType(Enum):
        """Enum for the LineageExtractionType property."""

        account_usage = "account_usage"
        information_schema = "information_schema"


class DB2FORDATASTAGE_CONNECTION:
    """Enums for properties in the DB2FORDATASTAGE connection."""

    class AuthenticationType(Enum):
        """Enum for the AuthenticationType property."""

        api_key = "api_key"
        username_and_password = "username_and_password"


class AMAZONRDS_ORACLE_CONNECTION:
    """Enums for properties in the AMAZONRDS_ORACLE connection."""

    class ConnectionMode(Enum):
        """Enum for the ConnectionMode property."""

        sid = "sid"
        service_name = "service_name"

    class FailoverMode(Enum):
        """Enum for the FailoverMode property."""

        connect = "connect"
        extended = "extended"
        select = "select"

    class MetadataDiscovery(Enum):
        """Enum for the MetadataDiscovery property."""

        no_remarks = "no_remarks"
        no_remarks_or_synonyms = "no_remarks_or_synonyms"
        no_synonyms = "no_synonyms"
        remarks_and_synonyms = "remarks_and_synonyms"

    class NumberType(Enum):
        """Enum for the NumberType property."""

        double = "double"
        varchar = "varchar"


class DB2ISERIES_CONNECTION:
    """Enums for properties in the DB2ISERIES connection."""

    class Db2iDriver(Enum):
        """Enum for the Db2iDriver property."""

        jcc = "jcc"
        jt400 = "jt400"


class AZURESYNAPSE_CONNECTION:
    """Enums for properties in the AZURESYNAPSE connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        entra_id_service = "entra_id_service"
        entra_id_user = "entra_id_user"
        user_credentials = "user_credentials"


class COGNOS_ANALYTICS_CONNECTION:
    """Enums for properties in the COGNOS_ANALYTICS connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        anonymous = "anonymous"
        username_apikey_namespace_cpdca = "username_apikey_namespace_cpdca"
        username_password_namespace_cpdca = "username_password_namespace_cpdca"
        cognos_analytics_apikey = "cognos_analytics_apikey"
        username_password_namespace = "username_password_namespace"


class ELASTICSEARCH_CONNECTION:
    """Enums for properties in the ELASTICSEARCH connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        apikey = "apikey"
        username_password = "username_password"


class SAPODATA_CONNECTION:
    """Enums for properties in the SAPODATA connection."""

    class AuthType(Enum):
        """Enum for the AuthType property."""

        api_key = "api_key"
        none = "none"
        basic = "basic"

    class SapOdataServiceVersion(Enum):
        """Enum for the SapOdataServiceVersion property."""

        V2 = "V2"
        V4 = "V4"


class AZURE_BLOB_STORAGE_CONNECTION:
    """Enums for properties in the AZURE_BLOB_STORAGE connection."""

    class AuthMethod(Enum):
        """Enum for the AuthMethod property."""

        connection_string = "connection_string"
        entra_id = "entra_id"
        entra_id_user = "entra_id_user"


class DATASTAX_CONNECTION:
    """Enums for properties in the DATASTAX connection."""

    class ReadConsistency(Enum):
        """Enum for the ReadConsistency property."""

        all = "all"
        local_one = "local_one"
        local_quorum = "local_quorum"
        local_serial = "local_serial"
        one = "one"
        quorum = "quorum"
        serial = "serial"
        three = "three"
        two = "two"

    class WriteConsistency(Enum):
        """Enum for the WriteConsistency property."""

        all = "all"
        any = "any"
        each_quorum = "each_quorum"
        local_one = "local_one"
        local_quorum = "local_quorum"
        local_serial = "local_serial"
        one = "one"
        quorum = "quorum"
        serial = "serial"
        three = "three"
        two = "two"


class FIELD:
    """Enums for FIELD."""

    class Fill(Enum):
        """Enum for the Fill property."""

        null = "null"
        space = 32

    class FinalDelim(Enum):
        """Enum for the FinalDelim property."""

        ws = "ws"
        end = "end"
        none = "none"
        null = "null"
        comma = ","
        tab = "\\\\t"

    class RecordDelim(Enum):
        """Enum for the RecordDelim property."""

        newline = "\n"
        null = "null"

    class RecordLength(Enum):
        """Enum for the RecordLength property."""

        fixed = "fixed"

    class RecordPrefix(Enum):
        """Enum for the RecordPrefix property."""

        one = 1
        two = 2
        four = 4

    class Format(Enum):
        """Enum for the Format property."""

        V = "V"
        VB = "VB"
        VS = "VS"
        VBS = "VBS"
        VR = "VR"

    class Delim(Enum):
        """Enum for the Delim property."""

        ws = "ws"
        end = "end"
        none = "none"
        null = "null"
        comma = ","
        tab = "\\t"

    class ValueSeparator(Enum):
        """Enum for the ValueSeparator property."""

        comma = ","

    class Prefix(Enum):
        """Enum for the Prefix property."""

        one = 1
        two = 2
        four = 4

    class Quote(Enum):
        """Enum for the Quote property."""

        single = "single"
        double = "double"
        none = "none"

    class VectorPrefix(Enum):
        """Enum for the VectorPrefix property."""

        one = 1
        two = 2
        four = 4

    class ByteOrder(Enum):
        """Enum for the ByteOrder property."""

        little_endian = "little_endian"
        big_endian = "big_endian"
        native_endian = "native_endian"

    class CharSet(Enum):
        """Enum for the CharSet property."""

        ebdic = "ebdic"
        ascii = "ascii"

    class DataFormat(Enum):
        """Enum for the DataFormat property."""

        binary = "binary"
        text = "text"

    class PadChar(Enum):
        """Enum for the PadChar property."""

        space = " "
        null = "null"

    class AllowAllZeros(Enum):
        """Enum for the AllowAllZeros property."""

        nofix_zero = "nofix_zero"
        fix_zero = "fix_zero"

    class DecimalSeparator(Enum):
        """Enum for the DecimalSeparator property."""

        comma = ","
        period = "."

    class PackedSigned(Enum):
        """Enum for the PackedSigned property."""

        true = True
        false = False

    class SignPosition(Enum):
        """Enum for the SignPosition property."""

        trailing = "trailing"
        leading = "leading"

    class Round(Enum):
        """Enum for the Round property."""

        ceil = "ceil"
        floor = "floor"
        round_inf = "round_inf"
        trunc_zero = "trunc_zero"

    class Unicode(Enum):
        """Enum for the Unicode property."""

        true = "Unicode"
        false = ""

    class CycleIncrement(Enum):
        """Enum for the CycleIncrement property."""

        one = 1
        part = "part"
        partcount = "partcount"

    class CycleLimit(Enum):
        """Enum for the CycleLimit property."""

        part = "part"
        partcount = "partcount"

    class CycleInitialValue(Enum):
        """Enum for the CycleInitialValue property."""

        zero = 0
        part = "part"
        partcount = "partcount"

    class GenerateType(Enum):
        """Enum for the GenerateType property."""

        cycle = "cycle"
        random = "random"

    class GenerateAlgorithm(Enum):
        """Enum for the GenerateAlgorithm property."""

        cycle = "cycle"
        alphabet = "alphabet"

    class RandomLimit(Enum):
        """Enum for the RandomLimit property."""

        partcount = "partcount"
        part = "part"

    class RandomSeed(Enum):
        """Enum for the RandomSeed property."""

        part = "part"

    class TimeExtendedType(Enum):
        """Enum for the TimeExtendedType property."""

        microseconds = "microseconds"
        timezone = "timezone"
        microseconds_and_timezone = "microseconds,timezone"

    class VectorType(Enum):
        """Enum for the VectorType property."""

        vector_occurs = "vector_occurs"
        variable = "variable"

    class DecimalPacked(Enum):
        """Enum for the DecimalPacked property."""

        packed = "packed"
        separate = "separate"
        zoned = "zoned"
        overpunch = "overpunch"

    class RecordType(Enum):
        """Enum for the RecordType property."""

        varying = "varying"
        implicit = "implicit"

    class FieldDelim(Enum):
        """Enum for the FieldDelim property."""

        ws = "ws"
        end = "end"
        none = "none"
        null = "null"
        comma = ","
        tab = "\\\\t"
