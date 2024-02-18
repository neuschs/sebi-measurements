import skrf as rf

female_female_thru = rf.Network('data/male_male_thru.s2p')
print(female_female_thru)
short_male = rf.Network('data/85052B_Short(f).s1p')
print(short_male)
short_male = short_male.interpolate(female_female_thru.frequency)
print(short_male)
female_female_thru_with_85052B_short_m = female_female_thru ** short_male
print(female_female_thru_with_85052B_short_m)

female_female_thru_with_85052B_short_m.write_touchstone('data/male_male_with_85052B_short.s1p')

female_female_thru_with_85052B_short_m.plot_s_db()