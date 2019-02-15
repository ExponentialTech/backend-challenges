import json
from collections import namedtuple

mu_purch = .5  # discounting factor associated with purchase of renewable energy
mu_max = .8  # max discounting factor
phi_prod = .005  # tonnes of CO2 per unit of renewable energy


def adjusted_total_emissions(company):
    c = company
    return (c.co2_tot - c.cc) * (1.0 - min(mu_purch * c.re_purch / c.e_tot, mu_max)) - phi_prod * c.re_prod


Company = namedtuple('Company', ['isin', 'co2_tot', 'cc', 're_purch', 're_prod', 'e_tot'])


def make_company(json_dict):
    d = json_dict
    return Company(
        isin=d['ISIN'],
        co2_tot=d['Total CO2 Equivalents Emissions'],
        cc=d['Carbon Credit Value'],
        re_purch=d['Renewable Energy Purchased'],
        re_prod=d['Renewable Energy Produced'],
        e_tot=float(d['Total Energy Use']),
    )


def test():
    # In the real world I would put these in a separate file and use
    # pytest, but this is quick to write and doesn't require
    # installing a third-party library.

    test_cases = [
        # (company, expected_score)

        # Manually-constructed tests of corner cases
        (Company(isin='', co2_tot=1, cc=0, re_purch=1, re_prod=0, e_tot=1), mu_purch),
        (Company(isin='', co2_tot=0, cc=1, re_purch=1, re_prod=0, e_tot=1), -mu_purch),
        (Company(isin='', co2_tot=1, cc=0, re_purch=0, re_prod=0, e_tot=1), 1),
        (Company(isin='', co2_tot=0, cc=0, re_purch=0, re_prod=0, e_tot=1), 0),
        (Company(isin='', co2_tot=0, cc=0, re_purch=0, re_prod=1, e_tot=1), -phi_prod),

        # Excercise the min(., mu_max) part by setting re_purch to
        # double the value of e_tot. Seems unlikely, but that's the
        # only way mu_max can be less than the other argument of
        # min. Not sure this formula really makes sense; maybe it was
        # supposed to generalize to any values of mu_purch and mu_max,
        # rather than just the values given in the spec, in which case
        # I should have made them parameters rather than constants.
        (Company(isin='', co2_tot=1, cc=0, re_purch=2, re_prod=0, e_tot=1), .2),

        # Test cases generated automatically from input data, to help
        # catch future regressions that we didn't think to test for
        # above
        (Company(isin=u'US0000000000', co2_tot=94972.49198, cc=8171.323352, re_purch=10576.00479, re_prod=96652.16115, e_tot=7000000.0), 86252.33570973662),
        (Company(isin=u'US0000000001', co2_tot=306900.6192, cc=57387.1, re_purch=31961.79405, re_prod=38372.1921, e_tot=80000000.0), 249271.81511629152),
        (Company(isin=u'US0000000002', co2_tot=171320.1651, cc=84303.7259, re_purch=62884.91047, re_prod=10689.83474, e_tot=153000000.0), 86945.10760476893),
        (Company(isin=u'US0000000003', co2_tot=2250.272892, cc=45713.96386, re_purch=12949.74785, re_prod=27468.66907, e_tot=226000000.0), -43599.78908361844),
        (Company(isin=u'US0000000004', co2_tot=132696.7376, cc=17515.5, re_purch=42559.65263, re_prod=69567.95366, e_tot=299000000.0), 114825.20038443955),
        (Company(isin=u'US0000000005', co2_tot=204269.3867, cc=26647.856, re_purch=9991.766644, re_prod=55829.34503, e_tot=372000000.0), 177339.9985543047),
        (Company(isin=u'US0000000006', co2_tot=64963.62994, cc=10556.11359, re_purch=9515.906056, re_prod=24720.73308, e_tot=445000000.0), 54283.33095784233),
        (Company(isin=u'US0000000007', co2_tot=89288.41927, cc=8902.593156, re_purch=32904.92748, re_prod=4051.865565, e_tot=518000000.0), 80363.01361071294),
        (Company(isin=u'US0000000008', co2_tot=59887.44837, cc=8838.602818, re_purch=4408.314004, re_prod=31232.14481, e_tot=591000000.0), 50892.49443933685),
        (Company(isin=u'US0000000009', co2_tot=270793.8773, cc=2135.478871, re_purch=6147.617183, re_prod=9418.298827, e_tot=664000000.0), 268610.0632533993),
        (Company(isin=u'US0000000010', co2_tot=436123.8946, cc=45901.30643, re_purch=61287.84832, re_prod=9800.114222, e_tot=737000000.0), 390157.36242738744),
        (Company(isin=u'US0000000011', co2_tot=219384.6241, cc=47047.32813, re_purch=18766.81362, re_prod=13746.23147, e_tot=810000000.0), 172266.56837937018),
        (Company(isin=u'US0000000012', co2_tot=907965.0176, cc=3432.989027, re_purch=11742.15742, re_prod=15078.18917, e_tot=883000000.0), 904450.6233816964),
        (Company(isin=u'US0000000013', co2_tot=63194.4312, cc=6784.725662, re_purch=76353.30911, re_prod=49.54423131, e_tot=956000000.0), 56407.20516638124),
        (Company(isin=u'US0000000014', co2_tot=58244.40199, cc=2965.056586, re_purch=898.2632691, re_prod=903570.7574, e_tot=1029000000.0), 50761.46748900898),
        (Company(isin=u'US0000000015', co2_tot=9657.810784, cc=83257.80621, re_purch=9985.097548, re_prod=14877.02366, e_tot=1102000000.0), -73674.04710367664),
        (Company(isin=u'US0000000016', co2_tot=8939.83813, cc=7357.74964, re_purch=10044.20882, re_prod=3664.637195, e_tot=1175000000.0), 1563.7585419708873),
        (Company(isin=u'US0000000017', co2_tot=294541.4886, cc=31341.08653, re_purch=29398.99459, re_prod=28384.09547, e_tot=1248000000.0), 263055.3815016257),
        (Company(isin=u'US0000000018', co2_tot=617044.557, cc=8289.310471, re_purch=15389.82384, re_prod=6266.641717, e_tot=1321000000.0), 608720.3672810487),
        (Company(isin=u'US0000000019', co2_tot=683013.3757, cc=9323.29235, re_purch=25050.59721, re_prod=3177.824916, e_tot=1394000000.0), 673668.1410192068),
    ]


    epsilon = 1e-18  # observed floating point approximation error
    for company, score in test_cases:
        assert adjusted_total_emissions(company) - score < epsilon, (company, score)

    try:
        c = Company(isin='', co2_tot=1, cc=1, re_purch=1, re_prod=1, e_tot=0)
        adjusted_total_emissions(c)
    except ZeroDivisionError:
        pass

    print "Tests passed"


def main():
    with open('data.json') as f:
        data = json.load(f)

    for company_dict in data:
        company = make_company(company_dict)
        print (company, adjusted_total_emissions(company))


if __name__ == '__main__':
    test()
    main()
