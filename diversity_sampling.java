import com.opencsv.CSVWriter;

import java.io.*;
import java.util.*;

public class diversity_sampling {

    private static final int SAMPLE_SIZE = 64;
    private static final float DEFAULT_NUMERIC_METRIC_SIMILARITY_THRESHOLD = 0.3f;
    // private static final float DEFAULT_NUMERIC_METRIC_SIMILARITY_THRESHOLD = 0.2f;
    private static HashMap<String, HashSet<Component>> cache = new HashMap<String, HashSet<Component>>();
    public static void main(String[] args) {
        try {
            HashSet<Component> universe = read_csv_from_file();
            HashSet<Component> sample = next_components(SAMPLE_SIZE, universe);
            float score = score_component(sample, universe);
            System.out.println(sample);
            System.out.println("Coverage score: " + score + " with sample size " + sample.size());
            write_to_csv(sample);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    private static void write_to_csv(HashSet<Component> sample) throws IOException {
        File file = new File("./unified_json/java_sample_new_2.csv");
        FileWriter outputfile = new FileWriter(file);

        CSVWriter writer = new CSVWriter(outputfile);

        String[] header = { "key", "repo_name", "size", "diameter", "density", "author_count", "comment_count", "repo_contributors", "component_url", "list_of_nodes"};
        writer.writeNext(header);
        for (Component entry: sample) {
            String[] row_entry = { Integer.toString(entry.key), 
                entry.repo_name, 
                Integer.toString(entry.size), 
                Integer.toString(entry.diameter), 
                Float.toString(entry.density),
                Integer.toString(entry.list_of_authors.size()),
                Integer.toString(entry.comment_count),
                Integer.toString(entry.repo_contributors),
                entry.component_url,
                String.join("|", entry.list_of_nodes)
                };
            writer.writeNext(row_entry);
        }
        writer.close();
    }

    private static float score_component(HashSet<Component> sample, HashSet<Component> universe) {
        HashSet<Component> coverage = new HashSet<Component>();
        for (Component component: sample) {
            HashSet<Component> similar_components = find_similar_components(component, universe);
            coverage.addAll(similar_components);
        }
        float score = (float) coverage.size() / universe.size();
        return score;
    }
    
    private static Boolean component_is_similar(Component a, Component b, float threshold) {
        Boolean is_similar;
        if (threshold == 0.0f) {
            threshold = DEFAULT_NUMERIC_METRIC_SIMILARITY_THRESHOLD;
        }
        is_similar = Math.abs(Math.log10(a.density) - Math.log10(b.density)) <= threshold && 
        Math.abs(Math.log10(a.diameter) - Math.log10(b.diameter)) <= threshold &&
        Math.abs(Math.log10(a.size) - Math.log10(b.size)) <= threshold && 
        Math.abs(Math.log10(a.list_of_authors.size()) - Math.log10(b.list_of_authors.size())) <= threshold &&
        Math.abs(Math.log10(Math.max(a.comment_count, 1)) - Math.log10(Math.max(b.comment_count, 1))) <= threshold;
        // true;

        return is_similar;
    }

    private static HashSet<Component> find_similar_components(Component component, HashSet<Component> universe) {
        HashSet<Component> similar_components = cache.get(Integer.toString(component.key));
        if (similar_components == null) {
            HashSet<Component> to_add = new HashSet<Component>();
            for (Component comparer : universe) {
                if (component_is_similar(component, comparer, DEFAULT_NUMERIC_METRIC_SIMILARITY_THRESHOLD)) {
                    to_add.add(comparer);
                }
            }
            cache.put(Integer.toString(component.key), to_add);
            return to_add;
        }
        return similar_components;
    }

    private static HashSet<Component> next_components(int K, HashSet<Component> component_universe) {
        HashSet<Component> sample = new HashSet<Component>();
        HashSet<Component> candidates = new HashSet<>(component_universe);
        HashSet<Component> c_space = new HashSet<>();
        Integer[] blocklist = new Integer[]{
            54915,
            18052,
            4869,
            36106,
            52493,
            40078,
            45584,
            63252,
            17046,
            58774,
            11032,
            58392,
            1433,
            49179,
            44062,
            39967,
            36000,
            52640,
            39974,
            16426,
            34730,
            20267,
            16428,
            430,
            34735,
            13361,
            58936,
            36152,
            185,
            23869,
            38589,
            16446,
            46143,
            17472,
            1985,
            17731,
            11717,
            37705,
            37322,
            44240,
            55505,
            4821,
            49494,
            25818,
            36060,
            30049,
            36194,
            62946,
            40802,
            25443,
            8679,
            16491,
            34155,
            24942,
            22130,
            34418,
            36212,
            16885,
            4854,
            22393,
            26745,
            123,
            383,
            56191
        };
        List<Integer> blocklistList = new ArrayList<>(Arrays.asList(blocklist));
        for (int i = 0; i < K; i++) {
            HashSet<Component> c_best = new HashSet<Component>();
            Component p_best = null;
            for (Component candidate: candidates) {
                if (!blocklistList.contains(candidate.key)) {
                    HashSet<Component> new_coverage_by_candidate = find_similar_components(candidate, candidates);
                    new_coverage_by_candidate.removeAll(c_space);
                    if (new_coverage_by_candidate.size() > c_best.size()) {
                        c_best = new_coverage_by_candidate;
                        p_best = candidate;
                    }
                }
            }
            if (p_best == null) {
                break;
            }
            sample.add(p_best);
            candidates.remove(p_best);
            c_space.addAll(c_best);
        }
        return sample;
    }

    private static HashSet<Component> read_csv_from_file() throws Exception {
        HashSet<Component> result = new HashSet<Component>();
        // BufferedReader br = new BufferedReader(new FileReader("./unified_json/result_test.csv"));
        BufferedReader br = new BufferedReader(new FileReader("./unified_json/result_simple.csv"));
        String line = "";
        br.readLine();
        while ((line = br.readLine()) != null) {
            String[] component_entry = line.split(",");
            HashSet<String> list_of_authors = new HashSet<>(Arrays.asList(component_entry[5].split("\\|")));
            ArrayList<String> list_of_nodes = new ArrayList<>(Arrays.asList(component_entry[9].split("\\|")));
            Component entry = new Component(Integer.parseInt(component_entry[0]), 
                                            component_entry[1],
                                            Integer.parseInt(component_entry[2]),
                                            Integer.parseInt(component_entry[3]),
                                            Float.parseFloat(component_entry[4]), 
                                            list_of_authors,
                                            component_entry[6],
                                            Integer.parseInt(component_entry[7]),
                                            Integer.parseInt(component_entry[8]),
                                            list_of_nodes
                                            );
            result.add(entry);
        }
        br.close();
        return result;
    }

}
