radius = 10
for dx in xrange(-radius, radius+1):
    for dy in xrange(max(-radius, -dx-radius), min(radius, -dx+radius)+1):
        print (dx, dy),
    print ''