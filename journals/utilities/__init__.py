def process_numbers(numberList):
    # split on commas
    result = []
    if isinstance(numberList, str):
        numberList = list( num.strip(',') for num in numberList.split() )
    if isinstance(numberList, int):
        numberList = [str(numberList)]
    for item in numberList:
        # if there is a dash then it is a range
        if "-" in item:
            item = [int(i) for i in item.split("-")]
            item.sort()
            if item[0] is not None:
                    result.extend(range(item[0], item[1]+1))
        else:
            result.extend([int(item)])

    result.sort()
    return result

def error(message):
    print
    print "#---------------------------------------------------------------------#"
    print "# ERROR:", message
    print "#---------------------------------------------------------------------#"
    print
    sys.exit()
