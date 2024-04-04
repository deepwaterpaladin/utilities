def merge_sort(arr) -> None:
  '''
  Sorts array in-place using merge sort algorithm.
  '''
  if len(arr) > 1:
        mid = len(arr)//2
        left = arr[:mid]
        right = arr[mid:]
        merge_sort(left)
        merge_sort(right)
        i = j = k = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            k += 1
        while i < len(left):
            arr[k] = left[i]
            i += 1
            k += 1
 
        while j < len(right):
            arr[k] = right[j]
            j += 1
            k += 1

def bubble_sort(arr) -> None:
  '''
  Sorts array in-place using bubble sort algorithm.
  '''
  n = len(arr)
    for i in range(n):
        swapped = False
        for k in range(0, n-i-1):
            if arr[k] > arr[k+1]:
                arr[k], arr[k+1] = arr[k+1], arr[k]
                swapped = True
        if swapped == False:
            break

def insertion_sort(arr) -> None:
  '''
  Sorts array in-place using insertion sort algorithm.
  '''
  for i in range(1, len(arr)):
        k = arr[i]
        j = i-1
        while j>= 0 and k < arr[j]:
            arr[j+1] = arr[j]
            j-=1
        arr[j+1] = k
