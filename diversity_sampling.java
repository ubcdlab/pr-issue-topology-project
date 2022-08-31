import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;

import com.opencsv.CSVWriter;

public class diversity_sampling {
    public static void main(String[] args) {
        try {
            HashSet<Component> universe = read_csv_from_file();
            HashSet<Component> sample = next_components(10, universe);
            float score = score_component(sample, universe);
            System.out.println(score);
            System.out.println(sample);
            write_to_csv(sample);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    private static void write_to_csv(ArrayList<Component> sample) throws IOException {
        File file = new File("./unified_json/java_sample.csv");
        FileWriter outputfile = new FileWriter(file);

        CSVWriter writer = new CSVWriter(outputfile);

        String[] header = { "key", "repo_name", "size", "diameter", "density"};
        writer.writeNext(header);
        for (int i = 0; i < sample.size(); i++) {
            Component entry = sample.get(i);
            String[] row_entry = { Integer.toString(entry.key), 
                entry.repo_name, 
                Integer.toString(entry.size), 
                Integer.toString(entry.diameter), 
                Float.toString(entry.density)};
            writer.writeNext(row_entry);
        }
        writer.close();
    }

    private static float score_component(ArrayList<Component> sample, ArrayList<Component> universe) {
        HashSet<Component> coverage = new HashSet<Component>();
        for (int i = 0; i < sample.size(); i++) {
            Component component = sample.get(i);
            ArrayList<Component> similar_components = find_similar_components(component, universe);
            coverage.addAll(similar_components);
        }
        float score = (float) coverage.size() / universe.size();
        return score;
    }
    
    private static Boolean component_is_similar(Component a, Component b, float threshold) {
        if (threshold == 0.0f) {
            assert(1 == 0);
            threshold = 0.5f;
        }
        Boolean is_similar = Math.abs(Math.log10(a.density) - Math.log10(b.density)) <= threshold && 
        Math.abs(Math.log10(a.diameter) - Math.log10(b.diameter)) <= threshold &&
        Math.abs(Math.log10(a.size) - Math.log10(b.size)) <= threshold &&
        // a.repo_name.equals(b.repo_name);
        true;
        return is_similar;
    }

    private static HashSet<Component> find_similar_components(Component component, HashSet<Component> universe) {
        HashSet<Component> similar_components = new HashSet<>();
        Iterator<Component> it = universe.iterator();
        while (it.hasNext()) {
            Component comparer = it.next();
            if (component_is_similar(component, comparer, 0.1f)) {
                similar_components.add(comparer);
            }
        }
        return similar_components;
    }

    private static ArrayList<Component> next_components(int K, ArrayList<Component> component_universe) {
        ArrayList<Component> sample = new ArrayList<Component>();
        ArrayList<Component> candidates = new ArrayList<>(component_universe);
        ArrayList<Component> c_space = new ArrayList<>();
        Component candidate;
        for (int i = 0; i < K; i++) {
            ArrayList<Component> c_best = new ArrayList<Component>();
            Component p_best = null;
            for (int j = 0; j < candidates.size(); j++) {
                candidate = candidates.get(j);
                ArrayList<Component> new_coverage_by_candidate = find_similar_components(candidate, candidates);
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
