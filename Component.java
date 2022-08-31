public class Component {
    int key;
    String repo_name;
    int size;
    int diameter;
    float density;
    
    public Component(int key, String repo_name, int size, int diameter, float density) {
        this.key = key;
        this.repo_name = repo_name;
        this.size = size;
        this.diameter = diameter;
        this.density = density;
    }

    @Override
    public String toString() {
        return this.key + " " + this.repo_name + " " + this.size + " " + this.density + " " + this.diameter;
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + key;
        result = prime * result + ((repo_name == null) ? 0 : repo_name.hashCode());
        return result;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj)
            return true;
        if (obj == null)
            return false;
        if (getClass() != obj.getClass())
            return false;
        Component other = (Component) obj;
        if (key != other.key)
            return false;
        if (repo_name == null) {
            if (other.repo_name != null)
                return false;
        } else if (!repo_name.equals(other.repo_name))
            return false;
        return true;
    }

    
}
