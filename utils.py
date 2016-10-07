
import error_handler

def parseInt(number):
    try:
        return int(number)
    except ValueError, e:
        error_handler.error("Invalid run numbers: %s" % str(e))

    return 0

def procNumbers(numberList):
    # simply see if it is an integer
    try:
        l = int(numberList)
        return [l]
    except ValueError:
        pass
    except TypeError:
        pass


    # split on commas
    result = []
    numberList = [ num for num in numberList.split() ]
    for item in numberList:
        # if there is a dash then it is a range
        if "-" in item:
            item = [parseInt(i) for i in item.split("-")]
            item.sort()
            if item[0] is not None:
                    result.extend(range(item[0], item[1]+1))
        else:
            item = parseInt(item)
            if item:
                result.append(item)

    result.sort()
    return result

