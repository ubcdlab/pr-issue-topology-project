import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.HashSet;
import com.opencsv.CSVWriter;

public class diversity_sampling {

    private static final int SAMPLE_SIZE = 50;
    private static final float DEFAULT_NUMERIC_METRIC_SIMILARITY_THRESHOLD = 0.1f;
    private static HashMap<String, HashSet<Component>> cache = new HashMap<String, HashSet<Component>>();
    public static void main(String[] args) {
        try {
            HashSet<Component> universe = read_csv_from_file();
            HashSet<Component> sample = next_components(SAMPLE_SIZE, universe);
            float score = score_component(sample, universe);
            System.out.println(score);
            System.out.println(sample);
            // write_to_csv(sample);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    private static void write_to_csv(HashSet<Component> sample) throws IOException {
        File file = new File("./unified_json/java_sample.csv");
        FileWriter outputfile = new FileWriter(file);

        CSVWriter writer = new CSVWriter(outputfile);

        String[] header = { "key", "repo_name", "size", "diameter", "density"};
        writer.writeNext(header);
        for (Component entry: sample) {
            String[] row_entry = { Integer.toString(entry.key), 
                entry.repo_name, 
                Integer.toString(entry.size), 
                Integer.toString(entry.diameter), 
                Float.toString(entry.density)};
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
        Math.abs(Math.log10(a.size) - Math.log10(b.size)) <= threshold;

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
        for (int i = 0; i < K; i++) {
            HashSet<Component> c_best = new HashSet<Component>();
            Component p_best = null;
            for (Component candidate: candidates) {
                HashSet<Component> new_coverage_by_candidate = find_similar_components(candidate, candidates);
                new_coverage_by_candidate.removeAll(c_space);
                if (new_coverage_by_candidate.size() > c_best.size()) {
                    c_best = new_coverage_by_candidate;
                    p_best = candidate;
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
            Component entry = new Component(Integer.parseInt(component_entry[0]), 
                                            component_entry[1],
                                            Integer.parseInt(component_entry[2]),
                                            Integer.parseInt(component_entry[3]),
                                            Float.parseFloat(component_entry[4]));
            result.add(entry);
        }
        br.close();
        return result;
    }

}
