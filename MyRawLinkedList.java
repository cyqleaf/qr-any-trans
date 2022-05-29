public class MyRawLinkedList {
    @SuppressWarnings("unused")
    private static final long serialVersionUID = 1561306366555780559L;

    static class Node {
        @SuppressWarnings("unused")
        private static final long serialVersionUID = -3505677833599614054L;
        String value;
        Node next = null;

        Node(String value, Node next) {
            this.value = value;
            this.next = next;
        }

        Node(String value) {
            this(value, null);
        }
    }

    /* This is intentionally left private so that you can't erroneously try to
     * instantiate a `new MyRawLinkedList()`
     */
    private MyRawLinkedList() {}

    /*
     * These methods included as examples for how to use Node as a linked list.
     */
    public static String listToString(Node head) {
        String ret = "";
        while (head != null) {
            ret += "\"" + head.value + (head.next == null ? "\" " : "\", ");
            head = head.next;
        }
        return "[ " + ret + "]";
    }

    public static void print(Node head) {
        System.out.println(listToString(head));
    }

    /*
     * Do not call this method in your code; it is not efficient. It is just for our
     * test cases.
     */
    public static String get(Node head, int index) {
        if (index < 0 || index >= size(head)) {
            throw new IndexOutOfBoundsException();
        } else {
            Node current = head;
            for (int i = 0; i < index; i++) {
                current = current.next;
            }
            return current.value;
        }
    }

    /* Do not call this method in your code. It is just for the test cases. */
    public static boolean contains(Node head, String value) {
        Node current = head;
        while (current != null) {
            if (current.value == value || current.value != null && current.value.equals(value)) {
                return true;
            }
            current = current.next;
        }
        return false;
    }

    /* Do not call this method in your code. It is just for the test cases. */
    public static int size(Node head) {
        int size = 0;
        Node current = head;
        while (current != null) {
            size++;
            current = current.next;
        }
        return size;
    }

    public static void main(String[] args) {
        Node list1 = new Node("One", new Node("Two", new Node("Three", null)));
        print(list1);

        Node args_as_list = null;
        for (int i = args.length - 1; i >= 0; i--)
            args_as_list = new Node(args[i], args_as_list);

        print(args_as_list);

        Node list2 = null;
        list2 = new Node("a", list2);
        list2 = new Node("b", list2);
        list2 = new Node("c", list2);
		list2 = new Node("xtreme", list2);
		list2 = new Node("apple", list2);
		list2 = new Node("xtreme", list2);
		list2 = new Node("b", list2);
		list2 = new Node("b", list2);
		list2 = new Node("hear", list2);
        print(list2);

		Node removedResult = removeMaximumValues(list2, -2);
		print(removedResult);

    }

    /*
     * Implement the methods below. Please do not change their signatures!
     */

    public static Node reverse(Node head) {
    	
        /* IMPLEMENT THIS METHOD! */
    	
    	if (head == null) {
    		return head;
    	}
    	if (head.next == null) {
    		return head;
    	}
    	
    	Node current = head;
    	Node prev = null;
    	
    	while(current != null) {
    		Node next = current.next;
    		current.next = prev;
    		prev = current;
    		current = next;
    	}
    	return prev;
    }

    public static Node removeMaximumValues(Node head, int N) {
    	
    	 /* IMPLEMENT THIS METHOD! */
    	
    	Node current = head;    
    	    	
    	//case 1 head is null
    	if(current == null) {
    		return null;
    	}
    	
    	//case 2 N < or = 0
    	if(N <= 0) {
    		return current;
    	}
		
		/**
		 * delete the max node for N times
		 */
    	for(int i =0; i < N; i++){

			// 暂存最大value的String
			String maxValue = current.value;

			// 用来遍历查找最大节点的value的指针
			Node currPoint = current;

			//遍历寻找最大前序节点
			while(currPoint.next != null){
				//找到真正最大节点值
				if(currPoint.next.value.compareTo(maxValue) >= 0){
					maxValue = currPoint.next.value;
				}
				currPoint = currPoint.next;
			}
			
			/**
			 * 查找并删除可能的同名节点
			 *  先保留头部节点维持列表形态，最后判断头部是否也要删除
			*/

			//恢复指针到头部
			currPoint = current;
			//删除中间的同名最大节点
			while(currPoint.next != null){
				if(currPoint.next.value.compareTo(maxValue) == 0){
					currPoint.next = currPoint.next.next;
				}else{
					currPoint = currPoint.next;
				}
			}
			//判断头部是否要删除
			if (current.value.compareTo(maxValue) == 0){
				current = current.next;
			}
			if(current == null){
				return null;
			}
		}
		
    	return current;
    }
    

    public static boolean containsSubsequence(Node head, Node other) {
    	
        /* IMPLEMENT THIS METHOD! */
    	
    	if(other == null) {
    		return true;
    	}
    	
    	if(head == null) {
    		return false;
    	}
    	
    	Node curr1 = other;
    	Node curr2 = head;
    	while(curr1 != null || curr2 != null) {
    		if(curr1.value != null && curr2.value != null) {
    			if(curr1.value == curr2.value) {
    				curr2 = curr2.next;
    			}
    			curr1 = curr1.next;   			
    		}
    	}
        return false;
    }
}
