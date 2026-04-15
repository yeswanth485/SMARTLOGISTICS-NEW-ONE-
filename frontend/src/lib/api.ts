import { OptimizeRequest, OptimizeResponse, PackingResult, ShipmentOption, ShipmentAnalysis, BoxCatalog } from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
    private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
        const url = `${API_BASE_URL}${endpoint}`;
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options?.headers,
            },
        });

        if (!response.ok) {
            let errorMsg = `HTTP Error ${response.status}`;
            try {
                const errorData = await response.json();
                errorMsg = errorData.detail || errorMsg;
            } catch (e) {}
            throw new Error(errorMsg);
        }

        return response.json();
    }

    async optimize(data: OptimizeRequest): Promise<OptimizeResponse> {
        return this.request<OptimizeResponse>('/optimize', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async uploadOptimize(file: File): Promise<OptimizeResponse> {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/optimize/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            let errorMsg = `HTTP Error ${response.status}`;
            try {
                const errorData = await response.json();
                errorMsg = errorData.detail || errorMsg;
            } catch (e) {}
            throw new Error(errorMsg);
        }

        return response.json();
    }

    async getPackingResult(orderId: string): Promise<PackingResult> {
        return this.request<PackingResult>(`/result/${orderId}`);
    }

    async getShipmentOptions(orderId: string): Promise<ShipmentOption[]> {
        return this.request<ShipmentOption[]>(`/shipment/${orderId}`);
    }

    async getShipmentAnalysis(orderId: string): Promise<ShipmentAnalysis> {
        return this.request<ShipmentAnalysis>(`/analysis/${orderId}`);
    }
    
    async getCatalog(): Promise<BoxCatalog[]> {
        return this.request<BoxCatalog[]>('/catalog/boxes');
    }
}

export const api = new ApiClient();
