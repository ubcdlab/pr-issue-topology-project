import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashSet;

/*
    int key;
    String repo_name;
    int size;
    int diameter;
    float density;
 */

public class diversity_sampling {
    public static void main(String[] args) {
        try {
            ArrayList<Component> universe = read_csv_from_file();
            ArrayList<Component> sample = next_components(100, universe);
            float score = score_component(sample, universe);
            System.out.println(score);
            System.out.println(sample);
            
        } catch (Exception e) {
            e.printStackTrace();
        }
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
            threshold = 0.5f;
        }

        return Math.log10(Math.abs(a.density - b.density)) <= threshold && 
        Math.log10(Math.abs(a.diameter - b.diameter)) <= threshold &&
        a.repo_name.equals(b.repo_name);
    }

    private static ArrayList<Component> find_similar_components(Component component, ArrayList<Component> universe) {
        ArrayList<Component> similar_components = new ArrayList<>();
        for (int i = 0; i < universe.size(); i++) {
            Component comparer = universe.get(i);
            if (component_is_similar(component, comparer, 0.5f)) {
                similar_components.add(comparer);
            }
        }
        return similar_components;
    }

    private static ArrayList<Component> next_components(int K, ArrayList<Component> component_universe) {
        ArrayList<Component> sample = new ArrayList<Component>();
        ArrayList<Component> candidates = new ArrayList<>(component_universe);
        ArrayList<Component> c_space = new ArrayList<>();
        for (int i = 0; i < K; i++) {
            ArrayList<Component> c_best = new ArrayList<Component>();
            Component p_best = null;
            for (int j = 0; j < candidates.size(); j++) {
                Component candidate = candidates.get(j);
                ArrayList<Component> coverage_by_candidate = find_similar_components(candidate, candidates);
                if (coverage_by_candidate.size() > c_best.size()) {
                    c_best = coverage_by_candidate;
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

    private static ArrayList<Component> read_csv_from_file() throws Exception {
        ArrayList<Component> result = new ArrayList<Component>();
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
