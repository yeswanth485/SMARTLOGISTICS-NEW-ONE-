export interface ProductInput {
    name: string;
    length: number;
    width: number;
    height: number;
    weight: number;
    quantity: number;
}

export interface OptimizeRequest {
    products: ProductInput[];
}

export interface ShipmentOption {
    id: string;
    order_id: string;
    carrier_name: string;
    estimated_cost: number;
    delivery_time: number;
    rating: number;
    status: string;
    tracking_id?: string;
    color?: string;
}

export interface OptimizeResponse {
    order_id: string;
    created_at: string;
    box_type: string;
    box_dimensions: string;
    utilization: number;
    packing_cost: number;
    items_count: number;
    total_cost: number;
    shipment_options: ShipmentOption[];
    best_option: string;
    reason: string;
    cost_saving: number;
    confidence: number;
}

export interface PackingResult {
    id: string;
    order_id: string;
    box_type: string;
    box_dimensions: string;
    utilization: number;
    cost: number;
    items_placed?: Array<any>;
    items_count: number;
}

export interface ShipmentAnalysis {
    id: string;
    order_id: string;
    best_option: string;
    reason: string;
    cost_saving: number;
    confidence: number;
}

export interface BoxCatalog {
    id: string;
    name: string;
    length: number;
    width: number;
    height: number;
    max_weight: number;
    base_cost: number;
}
