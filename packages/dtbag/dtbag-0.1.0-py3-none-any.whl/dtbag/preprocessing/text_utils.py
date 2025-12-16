class CatLists:
    
    def __init__(self):
        self.clusters_ = None
        self.representatives_ = None
    
    @staticmethod
    def _levenshtein_distance(s1, s2):

        if len(s1) < len(s2):
            return CatLists._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    @staticmethod
    def _similarity(s1, s2, threshold=0.7):
        
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return True
        
        distance = CatLists._levenshtein_distance(s1, s2)
        similarity_score = 1 - (distance / max_len)
        return similarity_score >= threshold
    
    @staticmethod
    def _find_most_common(items):
        
        if not items:
            return None
        
        frequency = {}
        max_count = 0
        most_common_item = items[0]
        
        for item in items:
            if item in frequency:
                frequency[item] += 1
            else:
                frequency[item] = 1
            
            if frequency[item] > max_count:
                max_count = frequency[item]
                most_common_item = item
        
        return most_common_item
    
    def fit_transform(self, items, threshold=0.7):
       
        if not items:
            self.clusters_ = []
            self.representatives_ = []
            return [], []
        
        n = len(items)
        clusters = []
        assigned = [False] * n
        
       
        for i in range(n):
            if not assigned[i]:
                current_cluster = [i]
                assigned[i] = True
                
                for j in range(i + 1, n):
                    if not assigned[j] and self._similarity(items[i], items[j], threshold):
                        current_cluster.append(j)
                        assigned[j] = True
                
                clusters.append(current_cluster)
        
        
        representatives = []
        for cluster in clusters:
            cluster_items = [items[idx] for idx in cluster]
            most_common = self._find_most_common(cluster_items)
            representatives.append(most_common)
        
        self.clusters_ = clusters
        self.representatives_ = representatives
        
        return clusters, representatives


class CatUnifier:
    
    def __init__(self):
        self.mapping_ = None
    
    def fit_transform(self, items, threshold=0.7):
        
        cat_lists = CatLists()
        clusters, representatives = cat_lists.fit_transform(items, threshold)
        
        unified = [None] * len(items)
        mapping = {}
        
        for cluster, rep in zip(clusters, representatives):
            for idx in cluster:
                unified[idx] = rep
                mapping[items[idx]] = rep
        
        self.mapping_ = mapping
        return unified
    
    def transform(self, new_items):
        
        if self.mapping_ is None:
            raise ValueError("first must call fit_transform")
        
        unified = []
        for item in new_items:
            if item in self.mapping_:
                unified.append(self.mapping_[item])
            else:
                unified.append(item)
        
        return unified
    
    def fit(self, items, threshold=0.7):
       
        _ = self.fit_transform(items, threshold)
        return self