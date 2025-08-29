'use client';

import React from 'react';

interface InvoiceItem {
  id: number;
  description: string;
  quantity: number;
  unit_cost: number;
}

interface Invoice {
  id: number;
  couple: {
    id: number;
    partner1_name: string;
    partner2_name: string;
  };
  invoice_number: string;
  invoice_date: string;
  invoice_ref: string;
  ceremony_date: string;
  venue: string;
  items: InvoiceItem[];
  gst: number;
  total: number;
}

interface InvoicePreviewModalProps {
  invoice: Invoice | null;
  isOpen: boolean;
  onClose: () => void;
}

const InvoicePreviewModal: React.FC<InvoicePreviewModalProps> = ({
  invoice,
  isOpen,
  onClose,
}) => {
  if (!isOpen || !invoice) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Invoice Preview</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <div className="space-y-4">
          <div className="border-b pb-4">
            <h3 className="text-lg font-semibold mb-2">Invoice #{invoice.invoice_number}</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium">Couple:</span> {invoice.couple.partner1_name} & {invoice.couple.partner2_name}
              </div>
              <div>
                <span className="font-medium">Total:</span> ${invoice.total}
              </div>
              <div>
                <span className="font-medium">Invoice Date:</span> {new Date(invoice.invoice_date).toLocaleDateString()}
              </div>
              <div>
                <span className="font-medium">Ceremony Date:</span> {new Date(invoice.ceremony_date).toLocaleDateString()}
              </div>
              <div>
                <span className="font-medium">Venue:</span> {invoice.venue}
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-medium mb-2">Items</h4>
            <div className="space-y-2">
              {invoice.items.map((item) => (
                <div key={item.id} className="flex justify-between text-sm">
                  <span>{item.description}</span>
                  <span>${item.quantity * item.unit_cost}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="border-t pt-4">
            <div className="flex justify-between text-sm">
              <span>Subtotal:</span>
              <span>${invoice.total - invoice.gst}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>GST:</span>
              <span>${invoice.gst}</span>
            </div>
            <div className="flex justify-between font-medium">
              <span>Total:</span>
              <span>${invoice.total}</span>
            </div>
          </div>
        </div>

        <div className="flex justify-end space-x-2 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
          >
            Close
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            Print Invoice
          </button>
        </div>
      </div>
    </div>
  );
};

export default InvoicePreviewModal; 