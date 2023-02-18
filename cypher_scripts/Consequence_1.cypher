// Consequence-1
match (i:issue {status:"closed"})<-[r {labels: "fixes"}]-(p:pull_request {status: "merged"}), (i2:issue)--(p)
where i2.creation_date > p.creation_date
return i, p, i2