//Consequence-1WProportion
match (i:issue {status:"closed"})-[r {labels: "fixes"}]-(p:pull_request {status: "merged"}), (i2:issue)--(p)
where i2.creation_date > p.creation_date
call apoc.path.subgraphAll(i, {limit: 50, bfs: true })
yield nodes, relationships
with i, nodes, [61, 167, 173, 210, 184, 291, 1036, 214, 429, 605, 600, 796, 816, 1586, 1006, 1102, 1152, 1209, 1329, 1824, 1760, 1861, 1883, 4154, 2279, 2547, 2211, 3371, 3595, 3725, 3685, 3985, 3923, 3996, 4145, 3800, 4598, 6106, 4473, 4649, 4774, 4970, 5973, 7116, 8636, 6643, 8557, 7644, 8355, 8163, 8240, 8372, 8371, 8498, 10733, 16061, 8992, 8734, 11904, 8997, 9007, 9190, 19335, 10705, 10432, 10640, 7235, 13431, 14625, 11398, 12144, 13282, 13313, 19608, 14746, 17287, 17752, 17785, 18922, 19761, 8591, 19883, 19901, 19950, 20010, 20146, 20064, 20228, 20304, 20527, 20347, 20406, 20424, 20526, 20730, 20729, 20778, 20804, 20808, 21113, 22054, 21290, 21459, 21264, 21639, 21437, 21416, 21636, 21940, 21634, 21673, 21968, 23005, 23369, 22736, 22844, 22904, 23540, 23506, 23509, 23588, 24404, 24816, 25012, 27119, 26374, 26285, 27227, 27232, 28075, 27677, 29838, 29455, 29319, 30162, 30032, 30110, 30098, 30168, 30184, 31047, 31151, 31845, 31268, 31704, 31278, 31299, 31516, 31335, 31409, 31439, 31461, 31537, 32115, 31490, 31521, 31610, 31614, 31656, 31691, 31977, 31723, 31833, 31960, 32268, 33352, 32048, 32056, 32005, 35286, 31939, 32028, 32041, 32100, 32098, 32217, 32157, 31434, 32162, 35229, 32845, 32271, 32365, 32601, 32286, 32285, 32431, 32327, 32363, 33223, 32835, 32653, 32477, 32473, 32486, 33423, 32549, 32607, 32659, 32709, 32766, 32841, 33047, 33284, 33143, 34223, 33666, 33655, 33629, 34972, 34489, 35373, 34893, 37066, 37046, 37057, 37079, 39405, 39726, 39615, 39677, 39749, 39739, 39772, 39747, 39811, 39992, 39879, 39883, 39891, 39909, 40074, 39937, 39936, 40091, 40000, 40027, 40196, 40151, 40296, 40309, 40331, 40395, 40361, 40346, 40437, 40602, 43741, 43976, 46004, 46170, 46351, 53546, 53635, 53799, 53990, 54628, 55403, 57852, 61678, 61688, 61687, 61674, 61685, 61707, 62006, 61721, 61845, 61969, 61846, 61794, 62116, 61806, 61956, 61998, 62042, 61996, 62008, 62016, 62010, 62011, 62366, 62067, 62106, 62078, 62145, 62097, 62152, 62126, 62138, 62144, 62176, 62381, 62173, 62148, 62181, 62153, 62233, 62265, 62420, 62270, 62556, 62498, 62497, 62380, 62303, 62291, 62293, 62327, 62668, 63347, 62580, 62653, 63728, 64737, 64839, 64841, 66000, 66189, 66194, 66193, 68307, 68405, 68395, 68415, 68453, 68463, 68472, 68995, 69019, 69745, 69721, 69972, 70051, 70168, 72668, 72849, 73140, 73194, 74729, 75960, 76101, 76035, 76108, 79010, 79841, 80675, 80037, 79962, 79809, 79884, 80176, 79879, 80000, 79999, 80084, 80048, 80235, 80645, 79934, 79964, 80077, 81296, 80057, 80649, 80226, 80105, 80120, 80155, 80192, 80453, 80232, 80335, 80456, 80646, 80416, 80321, 80776, 80493, 80574, 80563, 81090, 81334, 81150, 81569, 81810, 82171, 84112, 85549, 85543, 85545, 88646, 86643, 85872, 86701, 90119, 89279, 88156, 88869, 88649, 88864, 89477, 89331, 89374, 89373, 89541, 89759, 90129, 91466, 91505, 91970, 91944, 92084, 92281, 92468] as known_consq
with i, size(collect([i_node in nodes where i_node.type="issue" and i_node.status="closed" and i_node.number <> i.number and not id(i_node) in known_consq])) as not_consq, size(nodes) as len_nodes, nodes
return i, toFloat(not_consq) / toFloat(len_nodes) as proportion, nodes
