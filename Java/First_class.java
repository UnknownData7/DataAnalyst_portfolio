public class Main {
    
    public static void main(String[] args) {
        
        double price = 1000.0;    
        int count = 5;            
        boolean nds = true;   
        
        double total = calculatePrice(price, count, nds);
        
       
        System.out.println("Цена за штуку: " + price + " руб.");
        System.out.println("Количество: " + count + " шт.");
        System.out.println("НДС включен: " + (nds ? "да" : "нет"));
        System.out.println("Общая стоимость: " + total + " руб.");
    }
    
    public static double calculatePrice(double price, int count, boolean nds) {
        double total = price * count;  
        if (count >= 10) {
            total = total * 0.95;  
        }
        
        if (nds)
        {
            total = total * 1.20;  
        }
        
        return total;
    }
    
    public static double calculatePrice(double price, int count)
    {
        return calculatePrice(price, count, false);
    }
    
    public static double calculatePrice(int count, double price) {
        double total = price * count;
        
        if (count >= 10)
        {
            total = total * 0.95;
        }
        
        return total;
    }
}