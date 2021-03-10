def mark_as_complete(name):
    f = open(name,'w')
    f.write('Done')
    f.close()