# instruction to render the output to JSON format
render = 'JSON'
source = 'national'

# 64207-01
appnum_mask = [ "(\\d*\\-?[aABSIPQF]?)-(\\d{2})", "(\\d*)\\-?[aABSIPQF]?-(\\d{2})", "(\\d*)\\-?([aABSIPQF]?)-\\d{2}", "(\\d*)\\-?[aABSIPQF]?-\\d{2}", 
				"(\\d*)", "(\\d*)-\\d" ]
regnum_mask = [ "0*([1-9]*)", "(\\d*)" ]
