// Consequence-2
match (i:issue {status:"closed"})<-[r {labels: "fixes"}]-(p:pull_request {status: "merged"}), (i2:issue {status:"closed"})--(p), (i2)<--(p2:pull_request {status:"merged"})
where (i2.creation_date > p.creation_date or i2.creation_date > i.creation_date)
return i, p, i2, p2