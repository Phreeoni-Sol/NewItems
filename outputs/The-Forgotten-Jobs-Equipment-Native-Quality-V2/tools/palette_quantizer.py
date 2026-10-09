from collections import Counter
from weapon_codec import rgb555,rgba555

def quantize_words(colors,limit=15):
    # Farthest-color seeds preserve small accent colors that median-cut discarded.
    # Weighted Lloyd refinement is deterministic; this is palette encoding, not painting.
    histogram=Counter(rgb555(c) for c in colors)
    available=sorted(histogram)
    def dist(a,b):return sum((x-y)**2 for x,y in zip(rgba555(a)[:3],rgba555(b)[:3]))
    centers=[max(available,key=lambda w:(histogram[w],-w))]
    while len(centers)<min(limit,len(available)):
        centers.append(max((w for w in available if w not in centers),key=lambda w:(min(dist(w,c) for c in centers),histogram[w],-w)))
    for iteration in range(8):
        buckets=[[] for _ in centers]
        for word in available:
            j=min(range(len(centers)),key=lambda j:(dist(word,centers[j]),j))
            buckets[j].append(word)
        revised=[]
        for center,bucket in zip(centers,buckets):
            if not bucket:revised.append(center);continue
            total=sum(histogram[w] for w in bucket)
            average=tuple(round(sum(rgba555(w)[k]*histogram[w] for w in bucket)/total) for k in range(3))
            revised.append(rgb555(average))
        revised=list(dict.fromkeys(revised))
        while len(revised)<min(limit,len(available)):
            word=max(available,key=lambda w:(min(dist(w,c) for c in revised),histogram[w],-w))
            if word in revised:break
            revised.append(word)
        if revised==centers:break
        centers=revised
    return centers
